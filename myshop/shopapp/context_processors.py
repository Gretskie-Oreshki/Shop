# myshop/shopapp/context_processors.py
from .models import Wishlist, SiteSettings


def global_context(request):
    context = {}

    # Настройки сайта
    #context['site_settings'] = SiteSettings.get_settings()

    # Корзина
    if request.user.is_authenticated:
        from .models import Cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        context['cart_count'] = sum(item.quantity for item in cart.items.all())
    else:
        cart = request.session.get('cart', {})
        context['cart_count'] = sum(cart.values())

    # Избранное
    if request.user.is_authenticated:
        context['favorites_count'] = Wishlist.objects.filter(user=request.user).count()
    else:
        context['favorites_count'] = 0

    # Категории для меню
    from .models import Category
    context['all_categories'] = Category.objects.filter(is_active=True)
    context['hover_categories'] = Category.objects.filter(is_active=True)[:8]

    return context