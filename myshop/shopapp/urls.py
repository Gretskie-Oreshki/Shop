# myshop/shopapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # Аутентификация
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Каталог
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('category/<slug:slug>/', views.CatalogView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Поиск
    path('search/', views.SearchView.as_view(), name='search'),

    # Спецстраницы
    path('sales/', views.SalesView.as_view(), name='sales'),
    path('hits/', views.HitsView.as_view(), name='hits'),
    path('news/', views.NewsView.as_view(), name='news'),

    # Информационные
    path('about/', views.AboutView.as_view(), name='about'),
    path('delivery/', views.DeliveryView.as_view(), name='delivery'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('how-to-order/', views.HowToOrderView.as_view(), name='how-to-order'),
    path('returns/', views.ReturnsView.as_view(), name='returns'),
    path('faq/', views.FAQView.as_view(), name='faq'),

    # Корзина и избранное
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Заказы
    path('orders/', views.OrdersView.as_view(), name='orders'),

    # Подписка ← ДОБАВЬТЕ ЭТУ СТРОКУ
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
]