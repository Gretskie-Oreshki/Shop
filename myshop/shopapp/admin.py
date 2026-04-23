from django.contrib import admin
from .models import (
    Category, Product, ProductImage, Review, ReviewImage,
    Cart, CartItem, Order, OrderItem, UserProfile,
    Wishlist, Newsletter, Coupon, SiteSettings
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'is_available', 'is_hit']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'is_available', 'is_hit', 'is_new']
    search_fields = ['name', 'sku']
    inlines = [ProductImageInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']

admin.site.register(SiteSettings)