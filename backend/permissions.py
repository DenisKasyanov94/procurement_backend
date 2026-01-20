from rest_framework import permissions


class IsBuyer(permissions.BasePermission):
    """
    Разрешение только для покупателей.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'buyer'


class IsShop(permissions.BasePermission):
    """
    Разрешение только для магазинов.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'shop'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только владельцу объекта для редактирования.
    Для безопасных методов (GET, HEAD, OPTIONS) доступ открыт всем.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверяем, есть ли у объекта атрибут user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Для магазинов проверяем связь через user
        if hasattr(obj, 'shop') and hasattr(obj.shop, 'user'):
            return obj.shop.user == request.user
        
        return False
