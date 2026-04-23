# myshop/shopapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Avg, Count

from .models import (
    Product, Category, Review, Cart, CartItem,
    Order, OrderItem, UserProfile, Wishlist
)
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserEditForm


def index(request):
    """Главная страница"""
    products = Product.objects.filter(is_available=True)

    context = {
        'popular_categories': Category.objects.annotate(
            cnt=Count('products')
        ).filter(cnt__gt=0)[:8],
        'hit_products': products.filter(is_hit=True)[:8],
        'new_products': products.filter(is_new=True)[:8],
        'latest_reviews': Review.objects.filter(is_moderated=True)[:6],
    }
    return render(request, 'shopapp/index.html', context)


# ============ АУТЕНТИФИКАЦИЯ ============

class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    form_class = UserRegistrationForm
    template_name = 'shopapp/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Автоматический вход после регистрации
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать, {user.first_name}! Регистрация успешна.')
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """Вход в систему"""
    form_class = UserLoginForm
    template_name = 'shopapp/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Сессия закроется при закрытии браузера
            self.request.session.set_expiry(0)
        else:
            # Сессия на 2 недели
            self.request.session.set_expiry(1209600)

        messages.success(self.request, f'С возвращением, {form.get_user().first_name}!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('home'))


class CustomLogoutView(LogoutView):
    """Выход из системы"""
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы вышли из системы. До новых встреч!')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    """Профиль пользователя"""
    template_name = 'shopapp/profile.html'

    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'orders': Order.objects.filter(user=request.user)[:5],
            'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)


# ============ КАТАЛОГ ============

class CatalogView(ListView):
    """Каталог товаров"""
    model = Product
    template_name = 'shopapp/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        # Фильтрация
        category_ids = self.request.GET.getlist('categories')
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)

        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Сортировка
        sort = self.request.GET.get('sort', 'popular')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-sales_count')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            cnt=Count('products')
        ).filter(cnt__gt=0)
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'shopapp/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Увеличиваем счетчик просмотров
        product.views_count += 1
        product.save(update_fields=['views_count'])

        # Похожие товары
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]

        # Отзывы
        context['reviews'] = product.reviews.filter(is_moderated=True)

        # Проверка в избранном
        if self.request.user.is_authenticated:
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()

        return context


# ============ ИНФОРМАЦИОННЫЕ СТРАНИЦЫ ============

class AboutView(TemplateView):
    template_name = 'shopapp/about.html'


class DeliveryView(TemplateView):
    template_name = 'shopapp/delivery.html'


class ContactsView(TemplateView):
    template_name = 'shopapp/contacts.html'


class HowToOrderView(TemplateView):
    template_name = 'shopapp/how_to_order.html'


class ReturnsView(TemplateView):
    template_name = 'shopapp/returns.html'


class FAQView(TemplateView):
    template_name = 'shopapp/faq.html'


# ============ ПОИСК И СПЕЦСТРАНИЦЫ ============

class SearchView(ListView):
    """Поиск товаров"""
    model = Product
    template_name = 'shopapp/search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query),
                is_available=True
            )
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class SalesView(ListView):
    """Товары со скидками"""
    model = Product
    template_name = 'shopapp/sales.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(discount__gt=0, is_available=True)


class HitsView(ListView):
    """Хиты продаж"""
    model = Product
    template_name = 'shopapp/hits.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_hit=True, is_available=True)


class NewsView(ListView):
    """Новинки"""
    model = Product
    template_name = 'shopapp/news.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_new=True, is_available=True)


# ============ КОРЗИНА И ИЗБРАННОЕ ============

class FavoritesView(LoginRequiredMixin, TemplateView):
    """Избранное"""
    template_name = 'shopapp/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wishlist_items'] = Wishlist.objects.filter(
            user=self.request.user
        ).select_related('product')
        return context


class CartView(TemplateView):
    """Корзина"""
    template_name = 'shopapp/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            context['cart_items'] = cart.items.all()
            context['cart_total'] = sum(
                item.total_price for item in context['cart_items']
            )
        else:
            # Для неавторизованных - корзина в сессии
            cart = self.request.session.get('cart', {})
            items = []
            total = 0
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=int(product_id))
                    item_total = product.price * quantity
                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'total_price': item_total
                    })
                    total += item_total
                except Product.DoesNotExist:
                    pass
            context['cart_items'] = items
            context['cart_total'] = total
        return context


# myshop/shopapp/views.py

# myshop/shopapp/views.py

def add_to_cart(request, product_id):
    """Добавление в корзину"""
    from django.shortcuts import get_object_or_404, redirect

    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f'✅ {product.name} добавлен в корзину!')
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        messages.success(request, f'✅ {product.name} добавлен в корзину!')

    # Возвращаем туда, откуда пришли
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

def toggle_wishlist(request, product_id):
    """Добавление/удаление из избранного"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Необходимо авторизоваться'
        })

    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        wishlist_item.delete()
        in_wishlist = False
        message = f'{product.name} удален из избранного'
    else:
        in_wishlist = True
        message = f'{product.name} добавлен в избранное'

    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'message': message
    })


# ============ ЗАКАЗЫ ============

class OrdersView(LoginRequiredMixin, ListView):
    """История заказов"""
    model = Order
    template_name = 'shopapp/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class SubscribeView(View):
    """Подписка на рассылку"""

    def post(self, request):
        email = request.POST.get('email')
        if email:
            # Здесь можно сохранить email в базу данных
            # from .models import Newsletter
            # Newsletter.objects.get_or_create(email=email)
            messages.success(request, f'Спасибо! Вы подписались на рассылку с email: {email}')
        else:
            messages.error(request, 'Пожалуйста, введите email')

        return redirect('home')

    def get(self, request):
        return redirect('home')