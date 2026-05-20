# myshop/shopapp/recommendations.py (оставьте только SimpleRecommender, если DeepSeek не нужен)
from .models import Product, Cart, CartItem

class SimpleRecommender:
    """Простая рекомендательная система без API, с причинами"""

    def get_recommendations(self, user, max_recommendations=4):
        cart_categories = set()
        cart_product_ids = set()

        if user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
            if cart:
                cart_items = CartItem.objects.filter(cart=cart).select_related('product__category')
                cart_categories = {item.product.category_id for item in cart_items}
                cart_product_ids = {item.product_id for item in cart_items}

        # Если корзина пуста – ничего не рекомендуем
        if not cart_categories:
            return []

        # Рекомендации из тех же категорий
        qs = Product.objects.filter(
            category_id__in=cart_categories,
            is_available=True
        ).exclude(id__in=cart_product_ids).order_by('-sales_count', '-views_count')

        recs = []
        for product in qs[:max_recommendations]:
            recs.append({
                'product': product,
                'reason': f'В категории «{product.category.name}»'
            })

        # Добиваем хитами, если не хватает
        if len(recs) < max_recommendations:
            existing_ids = {r['product'].id for r in recs} | cart_product_ids
            additional = Product.objects.filter(
                is_hit=True, is_available=True
            ).exclude(id__in=existing_ids)[:max_recommendations - len(recs)]
            for p in additional:
                recs.append({'product': p, 'reason': 'Хит продаж'})

        return recs