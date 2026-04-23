# shopapp/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Category, Product, ProductImage
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Создает тестовые товары для магазина'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')

        # Создаем админа если нет
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@gretskieoreshki.ru',
                password='admin123',
                first_name='Администратор'
            )
            self.stdout.write(self.style.SUCCESS('Админ создан: admin / admin123'))

        # Создаем тестового пользователя
        if not User.objects.filter(username='user').exists():
            user = User.objects.create_user(
                username='user',
                email='user@mail.ru',
                password='user12345',
                first_name='Иван',
                last_name='Петров'
            )
            self.stdout.write(self.style.SUCCESS('Пользователь создан: user / user12345'))

        # Создаем категории
        categories_data = [
            {
                'name': 'Грецкие орехи',
                'slug': 'gretskie-orehi',
                'description': 'Отборные грецкие орехи из Греции',
                'icon': 'fas fa-utensils'
            },
            {
                'name': 'Миндаль',
                'slug': 'mindal',
                'description': 'Сладкий и ароматный миндаль',
                'icon': 'fas fa-leaf'
            },
            {
                'name': 'Фундук',
                'slug': 'funduk',
                'description': 'Лесные орехи высшего качества',
                'icon': 'fas fa-tree'
            },
            {
                'name': 'Фисташки',
                'slug': 'fistashki',
                'description': 'Отборные фисташки из Ирана',
                'icon': 'fas fa-seedling'
            },
            {
                'name': 'Кешью',
                'slug': 'keshyu',
                'description': 'Нежный и сливочный кешью',
                'icon': 'fas fa-moon'
            },
            {
                'name': 'Ореховые смеси',
                'slug': 'orehovye-smesi',
                'description': 'Готовые смеси орехов на любой вкус',
                'icon': 'fas fa-blender'
            },
            {
                'name': 'Сухофрукты',
                'slug': 'suhofrukty',
                'description': 'Натуральные сухофрукты без сахара',
                'icon': 'fas fa-apple-alt'
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'  Категория создана: {category.name}')

        # Создаем товары
        products_data = [
            # Грецкие орехи
            {
                'name': 'Грецкий орех очищенный, 500 г',
                'slug': 'gretskiy-oreh-ochischennyy-500g',
                'sku': 'GR-001',
                'category': 'gretskie-orehi',
                'description': 'Отборные очищенные грецкие орехи из Греции. Идеально подходят для выпечки, салатов и в качестве полезного перекуса.',
                'weight': '500 г',
                'weight_grams': 500,
                'price': 590,
                'old_price': 750,
                'stock': 100,
                'is_hit': True,
                'is_new': False,
                'has_express': True,
            },
            {
                'name': 'Грецкий орех в скорлупе, 1 кг',
                'slug': 'gretskiy-oreh-v-skorlupe-1kg',
                'sku': 'GR-002',
                'category': 'gretskie-orehi',
                'description': 'Свежие грецкие орехи в скорлупе. Долго сохраняют свежесть и полезные свойства.',
                'weight': '1 кг',
                'weight_grams': 1000,
                'price': 450,
                'stock': 200,
                'is_hit': True,
                'has_express': False,
            },
            {
                'name': 'Грецкий орех половинки, 250 г',
                'slug': 'gretskiy-oreh-polovinki-250g',
                'sku': 'GR-003',
                'category': 'gretskie-orehi',
                'description': 'Половинки грецкого ореха. Удобная фасовка для ежедневного использования.',
                'weight': '250 г',
                'weight_grams': 250,
                'price': 320,
                'stock': 150,
                'is_new': True,
                'has_express': True,
            },

            # Миндаль
            {
                'name': 'Миндаль сладкий очищенный, 300 г',
                'slug': 'mindal-sladkiy-ochischennyy-300g',
                'sku': 'MD-001',
                'category': 'mindal',
                'description': 'Отборный сладкий миндаль без кожицы. Идеальный источник витамина Е.',
                'weight': '300 г',
                'weight_grams': 300,
                'price': 420,
                'old_price': 520,
                'stock': 80,
                'is_hit': True,
                'has_express': True,
            },
            {
                'name': 'Миндаль жареный соленый, 200 г',
                'slug': 'mindal-zharenyy-solenyy-200g',
                'sku': 'MD-002',
                'category': 'mindal',
                'description': 'Хрустящий жареный миндаль с морской солью. Отличная закуска.',
                'weight': '200 г',
                'weight_grams': 200,
                'price': 350,
                'stock': 90,
                'is_new': True,
                'has_express': False,
            },

            # Фундук
            {
                'name': 'Фундук очищенный, 400 г',
                'slug': 'funduk-ochischennyy-400g',
                'sku': 'FD-001',
                'category': 'funduk',
                'description': 'Отборный очищенный фундук из Турции. Богат полезными жирами.',
                'weight': '400 г',
                'weight_grams': 400,
                'price': 480,
                'old_price': 600,
                'stock': 70,
                'is_hit': True,
                'has_express': True,
            },
            {
                'name': 'Фундук в шоколаде, 250 г',
                'slug': 'funduk-v-shokolade-250g',
                'sku': 'FD-002',
                'category': 'funduk',
                'description': 'Фундук в бельгийском молочном шоколаде. Изысканное лакомство.',
                'weight': '250 г',
                'weight_grams': 250,
                'price': 550,
                'stock': 60,
                'is_new': True,
                'has_express': False,
            },

            # Фисташки
            {
                'name': 'Фисташки жареные соленые, 500 г',
                'slug': 'fistashki-zharenye-solenye-500g',
                'sku': 'FS-001',
                'category': 'fistashki',
                'description': 'Отборные жареные фисташки с морской солью. Прямиком из Ирана.',
                'weight': '500 г',
                'weight_grams': 500,
                'price': 890,
                'old_price': 1100,
                'stock': 45,
                'is_hit': True,
                'has_express': True,
            },

            # Кешью
            {
                'name': 'Кешью очищенный, 300 г',
                'slug': 'keshyu-ochischennyy-300g',
                'sku': 'KS-001',
                'category': 'keshyu',
                'description': 'Нежный кешью из Индии. Сливочный вкус и минимум калорий.',
                'weight': '300 г',
                'weight_grams': 300,
                'price': 520,
                'stock': 55,
                'is_new': True,
                'has_express': True,
            },

            # Ореховые смеси
            {
                'name': 'Ореховая смесь "Здоровье", 500 г',
                'slug': 'orehovaya-smes-zdorove-500g',
                'sku': 'SM-001',
                'category': 'orehovye-smesi',
                'description': 'Сбалансированная смесь: грецкий орех, миндаль, фундук, кешью. Витаминный заряд на каждый день.',
                'weight': '500 г',
                'weight_grams': 500,
                'price': 650,
                'old_price': 790,
                'stock': 65,
                'is_hit': True,
                'has_express': True,
            },

            {
                'name': 'Смесь "Студенческая", 1 кг',
                'slug': 'smes-studencheskaya-1kg',
                'sku': 'SM-002',
                'category': 'orehovye-smesi',
                'description': 'Эконом-смесь: арахис, фундук, изюм. Доступная цена при отличном качестве.',
                'weight': '1 кг',
                'weight_grams': 1000,
                'price': 750,
                'stock': 85,
                'has_express': False,
            },
        ]

        for prod_data in products_data:
            category = categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'category': category,
                    'name': prod_data['name'],
                    'sku': prod_data['sku'],
                    'description': prod_data['description'],
                    'weight': prod_data['weight'],
                    'weight_grams': prod_data['weight_grams'],
                    'price': prod_data['price'],
                    'old_price': prod_data.get('old_price'),
                    'stock': prod_data['stock'],
                    'is_hit': prod_data.get('is_hit', False),
                    'is_new': prod_data.get('is_new', False),
                    'has_express': prod_data.get('has_express', False),
                }
            )
            if created:
                self.stdout.write(f'  Товар создан: {product.name}')

        self.stdout.write(self.style.SUCCESS('\nТестовые данные успешно созданы!'))
        self.stdout.write('\nДанные для входа:')
        self.stdout.write('  Админ: admin / admin123')
        self.stdout.write('  Пользователь: user / user12345')