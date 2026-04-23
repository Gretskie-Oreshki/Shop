from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True,
                              verbose_name='Изображение')
    icon = models.CharField(max_length=50, default='fas fa-box',
                            verbose_name='Иконка FontAwesome')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='Родительская категория')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    """Товары"""
    # Основная информация
    name = models.CharField(max_length=300, verbose_name='Название')
    slug = models.SlugField(max_length=300, unique=True, verbose_name='URL')
    sku = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    short_description = models.CharField(max_length=500, blank=True,
                                         verbose_name='Краткое описание')

    # Характеристики
    weight = models.CharField(max_length=50, verbose_name='Вес/Объем')  # например "500 г", "1 кг"
    weight_grams = models.IntegerField(default=0, verbose_name='Вес в граммах')
    country = models.CharField(max_length=100, default='Греция', verbose_name='Страна происхождения')
    composition = models.TextField(blank=True, verbose_name='Состав')
    nutritional_value = models.TextField(blank=True, verbose_name='Пищевая ценность')
    storage_conditions = models.TextField(blank=True, verbose_name='Условия хранения')
    shelf_life = models.CharField(max_length=100, blank=True, verbose_name='Срок годности')

    # Цены
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                    verbose_name='Старая цена')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         verbose_name='Закупочная цена')

    # Скидки и акции
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(99)],
                                   verbose_name='Скидка %')
    is_hit = models.BooleanField(default=False, verbose_name='Хит продаж')
    is_new = models.BooleanField(default=False, verbose_name='Новинка')

    # Наличие и доставка
    stock = models.IntegerField(default=0, verbose_name='Остаток на складе')
    is_available = models.BooleanField(default=True, verbose_name='Доступен для заказа')
    has_express = models.BooleanField(default=False, verbose_name='Экспресс-доставка')

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta Title')
    meta_description = models.TextField(max_length=300, blank=True, verbose_name='Meta Description')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='Meta Keywords')

    # Статистика
    views_count = models.IntegerField(default=0, verbose_name='Количество просмотров')
    sales_count = models.IntegerField(default=0, verbose_name='Количество продаж')

    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_hit', 'is_new']),
        ]

    def __str__(self):
        return f"{self.name} ({self.weight})"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Автоматический расчет скидки
        if self.old_price and self.old_price > self.price:
            self.discount = int((1 - self.price / self.old_price) * 100)
        else:
            self.old_price = None
            self.discount = 0

        # Автоопределение новинки (товары за последние 30 дней)
        from datetime import timedelta
        from django.utils import timezone
        if not self.pk:  # Если создается новый товар
            self.is_new = True

        super().save(*args, **kwargs)

    @property
    def avg_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def main_image(self):
        """Возвращает главное изображение или заглушку"""
        return self.images.filter(is_main=True).first() or self.images.first()

    @property
    def is_in_stock(self):
        return self.stock > 0 and self.is_available


class ProductImage(models.Model):
    """Изображения товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/%Y/%m/', verbose_name='Изображение')
    is_main = models.BooleanField(default=False, verbose_name='Главное изображение')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='Alt текст')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.product.name}"

    def save(self, *args, **kwargs):
        # Если это главное изображение, убираем флаг с других
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Review(models.Model):
    """Отзывы о товарах"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                 verbose_name='Оценка')
    text = models.TextField(verbose_name='Отзыв')
    advantages = models.TextField(blank=True, verbose_name='Достоинства')
    disadvantages = models.TextField(blank=True, verbose_name='Недостатки')
    is_moderated = models.BooleanField(default=False, verbose_name='Промодерирован')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Один отзыв от пользователя на товар

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"


class ReviewImage(models.Model):
    """Изображения к отзывам"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='images', verbose_name='Отзыв')
    image = models.ImageField(upload_to='reviews/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'


class Cart(models.Model):
    """Корзина"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Товары в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)],
                                   verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказы"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    PAYMENT_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличные при получении'),
        ('online', 'Онлайн-оплата'),
    ]

    DELIVERY_CHOICES = [
        ('courier', 'Курьером'),
        ('pickup', 'Самовывоз'),
        ('post', 'Почта России'),
    ]

    # Номер заказа
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заказа')

    # Покупатель
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='Покупатель')

    # Данные доставки
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес доставки')
    city = models.CharField(max_length=100, verbose_name='Город')
    postal_code = models.CharField(max_length=10, verbose_name='Почтовый индекс')

    # Способ доставки и оплаты
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES,
                                       default='courier', verbose_name='Способ доставки')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES,
                                      default='card', verbose_name='Способ оплаты')

    # Финансы
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма товаров')
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        verbose_name='Стоимость доставки')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name='Скидка')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итого')

    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new',
                              verbose_name='Статус')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')

    # Дополнительно
    comment = models.TextField(blank=True, verbose_name='Комментарий к заказу')

    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            # Генерация номера заказа: ORD-2026-XXXXX
            year = str(self.created_at.year) if self.created_at else '2026'
            code = ''.join(random.choices(string.digits, k=5))
            self.order_number = f"ORD-{year}-{code}"

        # Расчет итоговой суммы
        self.total = self.subtotal + self.delivery_cost - self.discount_amount

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Товары в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,
                                verbose_name='Товар')
    product_name = models.CharField(max_length=300, verbose_name='Название товара')
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.IntegerField(verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',
                                verbose_name='Пользователь')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True,
                               verbose_name='Аватар')
    birthday = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    address = models.TextField(blank=True, verbose_name='Адрес')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Индекс')

    # Бонусная программа
    bonus_points = models.IntegerField(default=0, verbose_name='Бонусные баллы')

    # Предпочтения
    receive_newsletters = models.BooleanField(default=True,
                                              verbose_name='Получать рассылку')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username}"


class Wishlist(models.Model):
    """Избранное"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Newsletter(models.Model):
    """Подписка на рассылку"""
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка на рассылку'
        verbose_name_plural = 'Подписки на рассылку'

    def __str__(self):
        return self.email


class Coupon(models.Model):
    """Купоны и промокоды"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код купона')
    discount = models.IntegerField(verbose_name='Скидка %')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name='Сумма скидки')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           verbose_name='Минимальная сумма заказа')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    valid_from = models.DateTimeField(verbose_name='Действует с')
    valid_to = models.DateTimeField(verbose_name='Действует до')
    usage_limit = models.IntegerField(default=0, verbose_name='Лимит использований')
    used_count = models.IntegerField(default=0, verbose_name='Использовано раз')

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and
                self.valid_from <= now <= self.valid_to and
                (self.usage_limit == 0 or self.used_count < self.usage_limit))


class SiteSettings(models.Model):
    """Настройки сайта"""
    site_name = models.CharField(max_length=200, default='GretskieOreshkiShop',
                                 verbose_name='Название сайта')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    address = models.TextField(verbose_name='Адрес')
    working_hours = models.CharField(max_length=200, verbose_name='Часы работы')

    # Доставка
    free_delivery_from = models.IntegerField(default=3000,
                                             verbose_name='Бесплатная доставка от (₽)')
    standard_delivery_cost = models.IntegerField(default=300,
                                                 verbose_name='Стоимость доставки (₽)')
    express_delivery_cost = models.IntegerField(default=500,
                                                verbose_name='Стоимость экспресс-доставки (₽)')

    # Соцсети
    vk_url = models.URLField(blank=True, verbose_name='ВКонтакте')
    telegram_url = models.URLField(blank=True, verbose_name='Telegram')
    whatsapp_url = models.URLField(blank=True, verbose_name='WhatsApp')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta Title')
    meta_description = models.TextField(max_length=300, blank=True,
                                        verbose_name='Meta Description')

    # Скрипты
    yandex_metrika = models.TextField(blank=True, verbose_name='Яндекс.Метрика (код)')
    google_analytics = models.TextField(blank=True, verbose_name='Google Analytics (код)')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        """Получить или создать настройки сайта"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings