# shopapp/management/commands/create_many_products.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Заполняет магазин 100+ тестовыми товарами разных категорий'

    def handle(self, *args, **options):
        self.stdout.write('Создание пользователей...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@shop.ru', 'admin123')
        if not User.objects.filter(username='user').exists():
            User.objects.create_user('user', 'user@mail.ru', 'user12345',
                                     first_name='Иван', last_name='Петров')

        # Категории
        cats = {
            'orehi': Category.objects.get_or_create(
                slug='orehi',
                defaults={'name': 'Орехи', 'description': 'Греческие орехи, сухофрукты', 'icon': 'fas fa-seedling'})[0],
            'futbolki': Category.objects.get_or_create(
                slug='futbolki',
                defaults={'name': 'Футболки', 'description': 'Оригинальные футболки с принтами', 'icon': 'fas fa-tshirt'})[0],
            'videoigry': Category.objects.get_or_create(
                slug='videoigry',
                defaults={'name': 'Видеоигры', 'description': 'Игры для PC и консолей', 'icon': 'fas fa-gamepad'})[0],
            'uslugi': Category.objects.get_or_create(
                slug='uslugi',
                defaults={'name': 'Услуги', 'description': 'Ремонт, чистка орехов, консультации', 'icon': 'fas fa-tools'})[0],
            'electronics': Category.objects.get_or_create(
                slug='electronics',
                defaults={'name': 'Электроника', 'description': 'Гаджеты, наушники, аксессуары', 'icon': 'fas fa-headphones'})[0],
            'sport': Category.objects.get_or_create(
                slug='sport',
                defaults={'name': 'Спорт', 'description': 'Товары для фитнеса и активного отдыха', 'icon': 'fas fa-running'})[0],
            'books': Category.objects.get_or_create(
                slug='books',
                defaults={'name': 'Книги', 'description': 'Кулинарные книги, фантастика', 'icon': 'fas fa-book'})[0],
            'souvenirs': Category.objects.get_or_create(
                slug='souvenirs',
                defaults={'name': 'Сувениры', 'description': 'Греческие сувениры, магниты', 'icon': 'fas fa-gift'})[0],
        }

        # Список товаров
        products_data = [
            # Орехи (уже были, можно оставить или дополнить)
            {'name': 'Грецкий орех очищенный, 500 г', 'slug': 'gretskiy-oreh-ochish-500', 'sku': 'GR-001', 'category': 'orehi',
             'description': 'Отборные очищенные грецкие орехи из Греции', 'weight': '500 г', 'weight_grams': 500,
             'price': 590, 'old_price': 750, 'stock': 100, 'is_hit': True},
            {'name': 'Миндаль сладкий очищенный, 300 г', 'slug': 'mindal-sladkiy-300', 'sku': 'MD-001', 'category': 'orehi',
             'description': 'Сладкий миндаль без кожицы', 'weight': '300 г', 'weight_grams': 300, 'price': 420,
             'old_price': 520, 'stock': 80, 'is_hit': True},
            {'name': 'Фундук очищенный, 400 г', 'slug': 'funduk-ochish-400', 'sku': 'FD-001', 'category': 'orehi',
             'description': 'Отборный очищенный фундук', 'weight': '400 г', 'weight_grams': 400, 'price': 480,
             'old_price': 600, 'stock': 70, 'is_hit': True},
            {'name': 'Фисташки жареные соленые, 500 г', 'slug': 'fistashki-zharenye-500', 'sku': 'FS-001',
             'category': 'orehi', 'description': 'Отборные фисташки с морской солью', 'weight': '500 г',
             'weight_grams': 500, 'price': 890, 'old_price': 1100, 'stock': 45, 'is_hit': True},
            {'name': 'Кешью очищенный, 300 г', 'slug': 'keshyu-ochish-300', 'sku': 'KS-001', 'category': 'orehi',
             'description': 'Нежный кешью из Индии', 'weight': '300 г', 'weight_grams': 300, 'price': 520,
             'stock': 55, 'is_new': True},
            {'name': 'Ореховая смесь "Здоровье", 500 г', 'slug': 'smes-zdorove-500', 'sku': 'SM-001',
             'category': 'orehi', 'description': 'Смесь грецкого ореха, миндаля, фундука', 'weight': '500 г',
             'weight_grams': 500, 'price': 650, 'old_price': 790, 'stock': 65, 'is_hit': True},
            {'name': 'Грецкий орех в скорлупе, 1 кг', 'slug': 'gretskiy-oreh-skorlupa-1kg', 'sku': 'GR-002',
             'category': 'orehi', 'description': 'Свежий урожай', 'weight': '1 кг', 'weight_grams': 1000, 'price': 450,
             'stock': 200, 'is_hit': True},
            {'name': 'Миндаль жареный, 200 г', 'slug': 'mindal-zharenyy-200', 'sku': 'MD-002', 'category': 'orehi',
             'description': 'Хрустящий миндаль', 'weight': '200 г', 'weight_grams': 200, 'price': 350, 'stock': 90,
             'is_new': True},
            {'name': 'Арахис жареный соленый, 500 г', 'slug': 'arahis-zharenyy-500', 'sku': 'AR-001', 'category': 'orehi',
             'description': 'Классический арахис к пиву', 'weight': '500 г', 'weight_grams': 500, 'price': 250,
             'stock': 150},
            {'name': 'Кедровые орешки очищенные, 100 г', 'slug': 'kedrovye-oreshki-100', 'sku': 'KO-001',
             'category': 'orehi', 'description': 'Сибирские кедровые орешки', 'weight': '100 г', 'weight_grams': 100,
             'price': 620, 'old_price': 750, 'stock': 30, 'is_new': True},

            # Футболки
            {'name': 'Футболка "Греческий орех"', 'slug': 'futbolka-grecheskiy-oreh', 'sku': 'FT-001',
             'category': 'futbolki', 'description': 'Хлопковая футболка с принтом грецкого ореха', 'weight': 'S-XXL',
             'weight_grams': 200, 'price': 1200, 'stock': 50, 'is_new': True},
            {'name': 'Футболка "Ореховый микс"', 'slug': 'futbolka-orehovy-mix', 'sku': 'FT-002', 'category': 'futbolki',
             'description': 'Яркий принт с разными орехами', 'weight': 'S-XXL', 'weight_grams': 200, 'price': 1100,
             'stock': 40},
            {'name': 'Футболка "Я люблю орехи"', 'slug': 'futbolka-ya-lyublyu-orehi', 'sku': 'FT-003',
             'category': 'futbolki', 'description': 'Надпись на русском', 'weight': 'S-XXL', 'weight_grams': 200,
             'price': 900, 'old_price': 1200, 'stock': 60, 'is_hit': True},
            {'name': 'Футболка "Ореховый гурман"', 'slug': 'futbolka-orehovy-gurman', 'sku': 'FT-004',
             'category': 'futbolki', 'description': 'Для ценителей', 'weight': 'M-XXL', 'weight_grams': 220,
             'price': 1300, 'stock': 35, 'is_new': True},
            {'name': 'Детская футболка "Орешек"', 'slug': 'detskaya-futbolka-oreshek', 'sku': 'FT-005',
             'category': 'futbolki', 'description': 'Мягкий хлопок для детей', 'weight': '98-140 см',
             'weight_grams': 150, 'price': 800, 'stock': 70},

            # Видеоигры
            {'name': 'Ореховый фермер (PC)', 'slug': 'orehovy-fermer-pc', 'sku': 'VG-001', 'category': 'videoigry',
             'description': 'Симулятор выращивания орехов', 'weight': 'Цифровой ключ', 'weight_grams': 0, 'price': 499,
             'stock': 999, 'is_new': True},
            {'name': 'Грецкий квест: В поисках сокровищ (PC)', 'slug': 'gretz-quest', 'sku': 'VG-002',
             'category': 'videoigry', 'description': 'Приключенческая игра', 'weight': 'Цифровой ключ',
             'weight_grams': 0, 'price': 799, 'old_price': 999, 'stock': 999},
            {'name': 'Ореховый тетрис (Android)', 'slug': 'orehovy-tetris', 'sku': 'VG-003', 'category': 'videoigry',
             'description': 'Мобильная головоломка', 'weight': 'APK-файл', 'weight_grams': 0, 'price': 199,
             'stock': 999, 'is_hit': True},
            {'name': 'Миндальный раннер (iOS)', 'slug': 'mindalny-runner', 'sku': 'VG-004', 'category': 'videoigry',
             'description': 'Бесконечный раннер', 'weight': 'App Store', 'weight_grams': 0, 'price': 299,
             'stock': 999},
            {'name': 'VR-орехобойка (Steam)', 'slug': 'vr-orehoboyka', 'sku': 'VG-005', 'category': 'videoigry',
             'description': 'Расколи орехи в виртуальной реальности', 'weight': 'Steam-ключ', 'weight_grams': 0,
             'price': 1499, 'stock': 500, 'is_new': True},
            {'name': 'Набор стикеров "Ореховые эмоции" (Telegram)', 'slug': 'stikery-orehi', 'sku': 'VG-006',
             'category': 'videoigry', 'description': 'Анимированные стикеры', 'weight': 'Цифровой товар',
             'weight_grams': 0, 'price': 99, 'stock': 9999},

            # Услуги
            {'name': 'Чистка грецких орехов (1 кг)', 'slug': 'chistka-orehov-1kg', 'sku': 'US-001', 'category': 'uslugi',
             'description': 'Профессиональная очистка от скорлупы', 'weight': 'Услуга', 'weight_grams': 0, 'price': 200,
             'stock': 100},
            {'name': 'Консультация по выбору орехов', 'slug': 'konsultaciya-po-oreham', 'sku': 'US-002',
             'category': 'uslugi', 'description': 'Часовая консультация эксперта', 'weight': 'Услуга',
             'weight_grams': 0, 'price': 1500, 'stock': 10},
            {'name': 'Обжарка орехов на заказ (1 кг)', 'slug': 'obzharka-orehov', 'sku': 'US-003', 'category': 'uslugi',
             'description': 'Обжарка с вашими специями', 'weight': 'Услуга', 'weight_grams': 0, 'price': 350,
             'stock': 50},
            {'name': 'Подарочная упаковка орехов', 'slug': 'podarochnaya-upakovka', 'sku': 'US-004', 'category': 'uslugi',
             'description': 'Красивая коробка с лентой', 'weight': 'Услуга', 'weight_grams': 0, 'price': 250,
             'stock': 500, 'is_hit': True},
            {'name': 'Мастер-класс "Ореховые десерты"', 'slug': 'master-klass-deserty', 'sku': 'US-005',
             'category': 'uslugi', 'description': 'Онлайн или офлайн', 'weight': 'Услуга', 'weight_grams': 0,
             'price': 3000, 'stock': 20, 'is_new': True},
            {'name': 'Ремонт орехоколов', 'slug': 'remont-orehokolov', 'sku': 'US-006', 'category': 'uslugi',
             'description': 'Ремонт и заточка', 'weight': 'Услуга', 'weight_grams': 0, 'price': 500, 'stock': 100},

            # Электроника
            {'name': 'Беспроводные наушники "NutPods"', 'slug': 'nutpods', 'sku': 'EL-001', 'category': 'electronics',
             'description': 'Bluetooth 5.0, 20 часов работы', 'weight': '50 г', 'weight_grams': 50, 'price': 2990,
             'old_price': 3990, 'stock': 30, 'is_hit': True},
            {'name': 'USB-флешка "Орех" 32 ГБ', 'slug': 'usb-oreh-32gb', 'sku': 'EL-002', 'category': 'electronics',
             'description': 'Корпус в виде грецкого ореха', 'weight': '10 г', 'weight_grams': 10, 'price': 890,
             'stock': 200, 'is_new': True},
            {'name': 'Чехол для телефона "Ореховый узор"', 'slug': 'chehol-orehovy-uzor', 'sku': 'EL-003',
             'category': 'electronics', 'description': 'Силиконовый чехол с рисунком', 'weight': '30 г',
             'weight_grams': 30, 'price': 590, 'stock': 150},
            {'name': 'Портативная колонка "OrehSound"', 'slug': 'orehsound', 'sku': 'EL-004', 'category': 'electronics',
             'description': 'Мощный звук, защита IPX7', 'weight': '300 г', 'weight_grams': 300, 'price': 2490,
             'stock': 25},
            {'name': 'Умные весы "NutriScale"', 'slug': 'nutriscale', 'sku': 'EL-005', 'category': 'electronics',
             'description': 'Измерение веса и пищевой ценности орехов', 'weight': '500 г', 'weight_grams': 500,
             'price': 3990, 'stock': 10, 'is_new': True},
            {'name': 'Электроотвертка с набором бит', 'slug': 'electrootvertka', 'sku': 'EL-006',
             'category': 'electronics', 'description': 'Аккумуляторная, 30 бит', 'weight': '400 г',
             'weight_grams': 400, 'price': 1890, 'stock': 40},

            # Спорт
            {'name': 'Эспандер "Ореховый хват"', 'slug': 'espander-orehovy', 'sku': 'SP-001', 'category': 'sport',
             'description': 'Для тренировки пальцев', 'weight': '100 г', 'weight_grams': 100, 'price': 490,
             'stock': 80, 'is_new': True},
            {'name': 'Бутылка для воды "Ореховая", 750 мл', 'slug': 'butylka-oreh-750', 'sku': 'SP-002',
             'category': 'sport', 'description': 'Спортивная бутылка с ореховым дизайном', 'weight': '100 г',
             'weight_grams': 100, 'price': 690, 'stock': 120},
            {'name': 'Йога-коврик "Миндаль"', 'slug': 'yoga-kovrik-mindal', 'sku': 'SP-003', 'category': 'sport',
             'description': 'Нескользящий, толщина 5 мм', 'weight': '1.2 кг', 'weight_grams': 1200, 'price': 1490,
             'old_price': 1990, 'stock': 35},
            {'name': 'Скакалка "Орех" регулируемая', 'slug': 'skakalka-oreh', 'sku': 'SP-004', 'category': 'sport',
             'description': 'Стальной трос, деревянные ручки', 'weight': '200 г', 'weight_grams': 200, 'price': 390,
             'stock': 200},
            {'name': 'Фитнес-браслет "NutBand"', 'slug': 'nutband', 'sku': 'SP-005', 'category': 'sport',
             'description': 'Шагомер, пульсометр, сон', 'weight': '20 г', 'weight_grams': 20, 'price': 1990,
             'stock': 60, 'is_hit': True},
            {'name': 'Гантели 2 кг "Орех" (пара)', 'slug': 'ganteli-oreh-2kg', 'sku': 'SP-006', 'category': 'sport',
             'description': 'Неопреновое покрытие', 'weight': '2 кг', 'weight_grams': 2000, 'price': 1290,
             'stock': 45},

            # Книги
            {'name': 'Книга "Орехи мира: путешествие гурмана"', 'slug': 'kniga-orehi-mira', 'sku': 'BK-001',
             'category': 'books', 'description': '240 страниц, твердый переплет', 'weight': '500 г',
             'weight_grams': 500, 'price': 1200, 'stock': 20, 'is_new': True},
            {'name': 'Кулинарная книга "100 рецептов с орехами"', 'slug': '100-receptov-s-orehami', 'sku': 'BK-002',
             'category': 'books', 'description': 'Цветные иллюстрации', 'weight': '400 г', 'weight_grams': 400,
             'price': 850, 'stock': 30, 'is_hit': True},
            {'name': 'Фантастика "Ореховая планета"', 'slug': 'fantastika-orehovaya', 'sku': 'BK-003',
             'category': 'books', 'description': 'Роман о приключениях на планете орехов', 'weight': '300 г',
             'weight_grams': 300, 'price': 650, 'stock': 15},
            {'name': 'Детская книга "Приключения Орешка"', 'slug': 'priklyucheniya-oreshka', 'sku': 'BK-004',
             'category': 'books', 'description': 'Иллюстрации, 48 стр.', 'weight': '200 г', 'weight_grams': 200,
             'price': 450, 'stock': 50},
            {'name': 'Бизнес-литература "Ореховый бизнес: от стартапа до успеха"', 'slug': 'orehovy-biznes',
             'sku': 'BK-005', 'category': 'books', 'description': 'Практическое руководство', 'weight': '350 г',
             'weight_grams': 350, 'price': 1500, 'stock': 10, 'is_new': True},
            {'name': 'Аудиокнига "Сказки орехового леса"', 'slug': 'audiokniga-orehi', 'sku': 'BK-006',
             'category': 'books', 'description': 'MP3, 3 часа', 'weight': 'Цифровой файл', 'weight_grams': 0,
             'price': 299, 'stock': 999},

            # Сувениры
            {'name': 'Магнит "Грецкий орех"', 'slug': 'magnit-greckiy-oreh', 'sku': 'SU-001', 'category': 'souvenirs',
             'description': 'Керамический магнит ручной работы', 'weight': '30 г', 'weight_grams': 30, 'price': 150,
             'stock': 300, 'is_hit': True},
            {'name': 'Брелок "Золотой орех"', 'slug': 'brelok-zolotoy-oreh', 'sku': 'SU-002', 'category': 'souvenirs',
             'description': 'Металлический брелок с позолотой', 'weight': '20 г', 'weight_grams': 20, 'price': 350,
             'stock': 150},
            {'name': 'Кружка "Ореховое настроение"', 'slug': 'kruzhka-orehovoe', 'sku': 'SU-003', 'category': 'souvenirs',
             'description': '330 мл, керамика', 'weight': '300 г', 'weight_grams': 300, 'price': 450, 'stock': 100,
             'is_new': True},
            {'name': 'Статуэтка "Ореховая сова"', 'slug': 'statuetka-orehovaya-sova', 'sku': 'SU-004',
             'category': 'souvenirs', 'description': 'Ручная работа из орехового дерева', 'weight': '150 г',
             'weight_grams': 150, 'price': 2200, 'stock': 10, 'is_new': True},
            {'name': 'Открытка "Ореховый привет"', 'slug': 'otkrytka-orehovy', 'sku': 'SU-005', 'category': 'souvenirs',
             'description': 'С конвертом', 'weight': '10 г', 'weight_grams': 10, 'price': 80, 'stock': 500},
            {'name': 'Сумка-шоппер "Ореховый рай"', 'slug': 'sumka-orehovy-ray', 'sku': 'SU-006',
             'category': 'souvenirs', 'description': 'Экосумка с принтом', 'weight': '100 г', 'weight_grams': 100,
             'price': 590, 'stock': 80},
            {'name': 'Чайная пара "Ореховый узор"', 'slug': 'chaynaya-para-orehi', 'sku': 'SU-007',
             'category': 'souvenirs', 'description': 'Фарфор, ручная роспись', 'weight': '400 г',
             'weight_grams': 400, 'price': 1200, 'stock': 15},
            {'name': 'Постер "Виды орехов" 30х40 см', 'slug': 'poster-vidy-orehov', 'sku': 'SU-008',
             'category': 'souvenirs', 'description': 'Плотная бумага, яркая печать', 'weight': '50 г',
             'weight_grams': 50, 'price': 350, 'stock': 40},
        ]

        self.stdout.write('Добавление товаров...')
        for p in products_data:
            cat = cats[p['category']]
            product, created = Product.objects.get_or_create(
                slug=p['slug'],
                defaults={
                    'category': cat,
                    'name': p['name'],
                    'sku': p['sku'],
                    'description': p.get('description', ''),
                    'weight': p['weight'],
                    'weight_grams': p['weight_grams'],
                    'price': p['price'],
                    'old_price': p.get('old_price'),
                    'stock': p['stock'],
                    'is_hit': p.get('is_hit', False),
                    'is_new': p.get('is_new', False),
                    'is_available': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Создано {Product.objects.count()} товаров!'))