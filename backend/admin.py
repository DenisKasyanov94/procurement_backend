from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Contact, Order,
    OrderItem, ConfirmEmailToken
)


class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'type',
        'company',
        'is_staff',
        'is_active')
    list_filter = ('type', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'company')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'company', 'position', 'type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': (
                'wide',), 'fields': (
                'email', 'password1', 'password2', 'first_name', 'last_name', 'type'), }), )


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state', 'user')
    list_filter = ('state',)
    search_fields = ('name', 'url')
    raw_id_fields = ('user',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_shops')
    search_fields = ('name',)
    filter_horizontal = ('shops',)

    def display_shops(self, obj):
        return ", ".join([shop.name for shop in obj.shops.all()])
    display_shops.short_description = 'Магазины'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    raw_id_fields = ('category',)


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'shop',
        'price',
        'price_rrc',
        'quantity',
        'external_id')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model', 'external_id')
    raw_id_fields = ('product', 'shop')


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('parameter',)
    search_fields = ('product_info__product__name', 'parameter__name', 'value')
    raw_id_fields = ('product_info', 'parameter')


class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'phone')
    list_filter = ('city',)
    search_fields = ('user__email', 'city', 'street', 'phone')
    raw_id_fields = ('user',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product_info',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'status', 'contact')
    list_filter = ('status', 'dt')
    search_fields = ('user__email', 'id')
    raw_id_fields = ('user', 'contact')
    inlines = [OrderItemInline]
    date_hierarchy = 'dt'


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product_info__product__name')
    raw_id_fields = ('order', 'product_info')


class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')
    search_fields = ('user__email', 'key')
    raw_id_fields = ('user',)


# Регистрация моделей в админке
admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ConfirmEmailToken, ConfirmEmailTokenAdmin)
