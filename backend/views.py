from rest_framework import viewsets, permissions
from .models import Shop, Category, Product, ProductInfo
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoSerializer


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра списка магазинов.
    Доступно только для чтения всем пользователям.
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра категорий товаров.
    Доступно только для чтения всем пользователям.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра товаров.
    Доступно только для чтения всем пользователям.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра информации о товарах (цены, наличие в магазинах).
    Доступно только для чтения всем пользователям.
    """
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('product_parameters')
    serializer_class = ProductInfoSerializer
    permission_classes = [permissions.AllowAny]
