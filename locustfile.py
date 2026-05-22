"""
Нагрузочное тестирование GretskieOreshkiShop
=============================================
Запуск:
    locust -f locustfile.py --host=http://localhost:8000

Классы пользователей:
    - GuestUser       — незарегистрированный посетитель (просмотр, поиск, корзина)
    - RegisteredUser  — авторизованный покупатель (полный цикл покупки)
    - BounceUser      — «отказник» (зашёл на главную и ушёл)
"""

import re
import random
from locust import HttpUser, task, between, events


# ─────────────────────────────────────────────
# Общие данные
# ─────────────────────────────────────────────

SEARCH_QUERIES = ["грецкий", "миндаль", "фундук", "смесь", "орех", "кешью", "фисташки"]

FALLBACK_SLUGS = [
    "gretskiy-oreh-ochischennyy-500g",
    "gretskiy-oreh-v-skorlupe-1kg",
    "gretskiy-oreh-polovinki-250g",
    "mindal-sladkiy-ochischennyy-300g",
    "mindal-zharenyy-solenyy-200g",
    "funduk-ochischennyy-400g",
    "funduk-v-shokolade-250g",
    "fistashki-zharenye-solenye-500g",
    "keshyu-ochischennyy-300g",
    "orehovaya-smes-zdorove-500g",
    "orehovaya-smes-zdorove-500g",
    "smes-studencheskaya-1kg",
]

FALLBACK_PRODUCT_IDS = list(range(1, 13))

CATEGORY_SLUGS = [
    "gretskie-orehi",
    "mindal",
    "funduk",
    "fistashki",
    "keshyu",
    "orehovye-smesi",
    "suhofrukty",
]

INFO_PAGES = ["/about/", "/delivery/", "/contacts/", "/faq/", "/returns/", "/how-to-order/"]


# ─────────────────────────────────────────────
# Базовый миксин: CSRF, парсинг страниц
# ─────────────────────────────────────────────

class ShopMixin:
    """Вспомогательные методы, общие для всех классов пользователей."""

    def _csrf(self, url: str) -> str:
        """Открывает страницу и возвращает CSRF-токен (из формы или куки)."""
        resp = self.client.get(url, name=url)
        if resp.status_code != 200:
            return self.client.cookies.get("csrftoken", "")
        m = re.search(
            r'<input[^>]+name=["\']csrfmiddlewaretoken["\'][^>]+value=["\']([^"\']+)["\']',
            resp.text,
        )
        return m.group(1) if m else self.client.cookies.get("csrftoken", "")

    def _post(self, url: str, data: dict = None, name: str = None):
        """POST с автоматическим добавлением CSRF-токена."""
        token = self._csrf(url)
        payload = dict(data or {})
        payload["csrfmiddlewaretoken"] = token
        return self.client.post(url, data=payload, name=name or url)

    def _fetch_product_slugs(self) -> list:
        """Собирает слаги товаров со страницы каталога."""
        resp = self.client.get("/catalog/", name="/catalog/")
        if resp.status_code == 200:
            found = list(set(re.findall(r'href=["\']/product/([^"\']+)/["\']', resp.text)))
            if found:
                return found
        return FALLBACK_SLUGS

    def _fetch_product_ids(self) -> list:
        """Собирает ID товаров из data-атрибутов кнопок «В корзину»."""
        resp = self.client.get("/catalog/", name="/catalog/")
        if resp.status_code == 200:
            found = re.findall(r'data-product-id=["\'](\d+)["\']', resp.text)
            if found:
                return [int(i) for i in set(found)]
        return FALLBACK_PRODUCT_IDS


# ─────────────────────────────────────────────
# 1. Незарегистрированный посетитель
# ─────────────────────────────────────────────

class GuestUser(ShopMixin, HttpUser):
    """
    Сценарий: анонимный посетитель.
    Просматривает сайт, ищет товары, добавляет в корзину без входа.
    Вес 50 — половина трафика.
    """
    weight = 50
    wait_time = between(1, 3)

    def on_start(self):
        self.product_slugs = self._fetch_product_slugs()
        self.product_ids = self._fetch_product_ids()

    # ── Просмотр ──────────────────────────────

    @task(8)
    def view_home(self):
        """Главная страница."""
        self.client.get("/", name="/")

    @task(6)
    def browse_catalog(self):
        """Каталог без фильтров."""
        self.client.get("/catalog/", name="/catalog/")

#
#    @task(4)
#    def browse_catalog_with_sort(self):
#        """Каталог с сортировкой."""
#        sort = random.choice(["price_asc", "price_desc", "new", "popular"])
#        self.client.get(f"/catalog/?sort={sort}", name="/catalog/?sort=")

#    @task(3)
#    def browse_category(self):
#        """Просмотр категории."""
#        slug = random.choice(CATEGORY_SLUGS)
#        self.client.get(f"/category/{slug}/", name="/category/<slug>/")

    @task(5)
    def view_product(self):
        """Страница товара."""
        slug = random.choice(self.product_slugs)
        self.client.get(f"/product/{slug}/", name="/product/<slug>/")

    @task(3)
    def search_products(self):
        """Поиск товаров."""
        q = random.choice(SEARCH_QUERIES)
        self.client.get(f"/search/?q={q}", name="/search/")

    @task(2)
    def view_info_page(self):
        """Информационная страница (О нас, Доставка, FAQ…)."""
        page = random.choice(INFO_PAGES)
        self.client.get(page, name="/about/")

    @task(2)
    def view_sales(self):
        self.client.get("/sales/", name="/sales/")

    @task(2)
    def view_hits(self):
        self.client.get("/hits/", name="/hits/")

    @task(1)
    def view_news(self):
        self.client.get("/news/", name="/news/")

    # ── Корзина (сессионная) ──────────────────

    @task(3)
    def add_to_cart_guest(self):
        """Добавление в корзину без авторизации (сессия)."""
        pid = random.choice(self.product_ids)
        self._post(
            f"/cart/add/{pid}/",
            name="/cart/add/<id>/",
        )

    @task(2)
    def view_cart(self):
        self.client.get("/cart/", name="/cart/")

    # ── Регистрация / Вход ────────────────────

    @task(1)
    def view_login_page(self):
        self.client.get("/login/", name="/login/")

    @task(1)
    def view_register_page(self):
        self.client.get("/register/", name="/register/")

    # ── Подписка ─────────────────────────────

    @task(1)
    def subscribe_newsletter(self):
        """Подписка на рассылку с главной страницы."""
        rand = random.randint(100000, 999999)
        self._post(
            "/subscribe/",
            data={"email": f"guest{rand}@loadtest.com"},
            name="/subscribe/",
        )


# ─────────────────────────────────────────────
# 2. Авторизованный покупатель
# ─────────────────────────────────────────────

class RegisteredUser(ShopMixin, HttpUser):
    """
    Сценарий: зарегистрированный пользователь.
    Полный цикл: регистрация → каталог → товар → корзина → избранное → профиль.
    Вес 40.
    """
    weight = 40
    wait_time = between(1, 3)

    def on_start(self):
        self.uid = random.randint(10000, 99999)
        self.username = f"loadtest_{self.uid}"
        self.password = "Test123456!"
        self.product_slugs = self._fetch_product_slugs()
        self.product_ids = self._fetch_product_ids()
        self._register_or_login()

    # ── Авторизация ───────────────────────────

    def _register_or_login(self):
        """Сначала пытаемся зарегистрироваться, при неудаче — войти под тестовым юзером."""
        resp = self._post(
            "/register/",
            data={
                "username": self.username,
                "email": f"{self.username}@loadtest.com",
                "first_name": "Нагрузка",
                "last_name": "Тест",
                "phone": "+79990000000",
                "password1": self.password,
                "password2": self.password,
            },
            name="/register/ [signup]",
        )
        # Если редирект прошёл — регистрация успешна
        if resp and resp.status_code in (200, 302):
            return
        # Иначе входим под заранее созданным пользователем
        self._login_as_test_user()

    def _login_as_test_user(self):
        self._post(
            "/login/",
            data={"username": "user", "password": "user12345"},
            name="/login/ [test-user]",
        )

    def _logout(self):
        self._post("/logout/", name="/logout/")

    # ── Сценарий: полный просмотр ──────────────

    @task(6)
    def scenario_browse_and_add(self):
        """
        Полный сценарий: главная → каталог → товар → добавить в корзину.
        """
        self.client.get("/", name="/")
        self.client.get("/catalog/", name="/catalog/")
        slug = random.choice(self.product_slugs)
        self.client.get(f"/product/{slug}/", name="/product/<slug>/")
        pid = random.choice(self.product_ids)
        self._post(f"/cart/add/{pid}/", name="/cart/add/<id>/")
        self.client.get("/cart/", name="/cart/")

    @task(4)
    def scenario_search_and_view(self):
        """Поиск → переход на товар."""
        q = random.choice(SEARCH_QUERIES)
        resp = self.client.get(f"/search/?q={q}", name="/search/")
        if resp.status_code == 200:
            slugs = re.findall(r'href=["\']/product/([^"\']+)/["\']', resp.text)
            if slugs:
                self.client.get(f"/product/{random.choice(slugs)}/", name="/product/<slug>/ [from search]")

    @task(3)
    def scenario_category_browsing(self):
        """Просмотр категории → несколько товаров."""
        slug = random.choice(CATEGORY_SLUGS)
        resp = self.client.get(f"/category/{slug}/", name="/category/<slug>/")
        if resp.status_code == 200:
            found = re.findall(r'href=["\']/product/([^"\']+)/["\']', resp.text)
            for s in random.sample(found, min(2, len(found))):
                self.client.get(f"/product/{s}/", name="/product/<slug>/ [from category]")

    @task(3)
    def scenario_wishlist(self):
        """Добавление товара в избранное и просмотр списка."""
        pid = random.choice(self.product_ids)
        self.client.get(
            f"/wishlist/toggle/{pid}/",
            name="/wishlist/toggle/<id>/",
        )
        self.client.get("/favorites/", name="/favorites/")

    # ── Отдельные задачи ──────────────────────

    @task(5)
    def view_home(self):
        self.client.get("/", name="/")

    @task(4)
    def browse_catalog(self):
        self.client.get("/catalog/", name="/catalog/")

    @task(3)
    def view_product(self):
        slug = random.choice(self.product_slugs)
        self.client.get(f"/product/{slug}/", name="/product/<slug>/")

    @task(2)
    def view_cart(self):
        self.client.get("/cart/", name="/cart/")

    @task(2)
    def view_profile(self):
        self.client.get("/profile/", name="/profile/")

    @task(2)
    def view_orders(self):
        self.client.get("/orders/", name="/orders/")

    @task(2)
    def view_favorites(self):
        self.client.get("/favorites/", name="/favorites/")

    @task(1)
    def view_sales(self):
        self.client.get("/sales/", name="/sales/")

    @task(1)
    def view_hits(self):
        self.client.get("/hits/", name="/hits/")

    @task(1)
    def subscribe_newsletter(self):
        self._post(
            "/subscribe/",
            data={"email": f"reg{self.uid}@loadtest.com"},
            name="/subscribe/",
        )


# ─────────────────────────────────────────────
# 3. «Отказник» — пришёл и сразу ушёл
# ─────────────────────────────────────────────

class BounceUser(ShopMixin, HttpUser):
    """
    Сценарий: посетитель с высоким показателем отказов.
    Заходит на 1–2 страницы и уходит. Вес 10.
    """
    weight = 10
    wait_time = between(1, 3)

    def on_start(self):
        self.product_slugs = self._fetch_product_slugs()

    @task(5)
    def just_home(self):
        """Только главная страница."""
        self.client.get("/", name="/")

    @task(3)
    def home_then_catalog(self):
        """Главная → каталог → уход."""
        self.client.get("/", name="/")
        self.client.get("/catalog/", name="/catalog/")

    @task(2)
    def direct_product(self):
        """Прямой переход на товар (например, из рекламы)."""
        slug = random.choice(self.product_slugs)
        self.client.get(f"/product/{slug}/", name="/product/<slug>/ [direct]")

    @task(1)
    def info_page(self):
        """Информационная страница."""
        self.client.get(random.choice(INFO_PAGES), name="/info-page/")