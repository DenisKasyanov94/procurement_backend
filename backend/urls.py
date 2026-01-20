from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'shops', views.ShopViewSet, basename='shop')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'product-info', views.ProductInfoViewSet, basename='product-info')
router.register(r'basket', views.BasketViewSet, basename='basket')

urlpatterns = [
    path('', include(router.urls)),
    
    # Аутентификация и пользователи
    path('user/register/', views.UserRegisterView.as_view(), name='user-register'),
    path('user/login/', views.user_login, name='user-login'),
    path('user/logout/', views.user_logout, name='user-logout'),
    path('user/profile/', views.user_profile, name='user-profile'),
    
    # Для магазинов
    path('partner/update/', views.PartnerUpdate.as_view(), name='partner-update'),
]
