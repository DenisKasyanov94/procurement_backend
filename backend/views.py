from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from .models import Shop, Category, Product, ProductInfo
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoSerializer, UserLoginSerializer, UserProfileSerializer, UserRegisterSerializer
from .permissions import IsBuyer, IsShop

# ==================== VIEWSETS ДЛЯ КАТАЛОГА ====================

class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра списка магазинов.
    Доступ: чтение - всем, запись - только авторизованным.
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра категорий товаров.
    Доступ: чтение - всем, запись - только авторизованным.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра товаров.
    Доступ: чтение - всем, запись - только авторизованным.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра информации о товарах (цены, наличие в магазинах).
    Доступ: чтение - всем, запись - только авторизованным.
    """
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('product_parameters')
    serializer_class = ProductInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ==================== РЕГИСТРАЦИЯ ====================

class UserRegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "status": True,
                "message": "Пользователь успешно создан.",
                "user_id": user.id
            },
            status=status.HTTP_201_CREATED
        )


# ==================== АУТЕНТИФИКАЦИЯ ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    Вход пользователя и получение токена.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        from django.contrib.auth import authenticate

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)

        if user:
            if not user.is_active:
                return Response(
                    {'status': False, 'error': 'Пользователь не активирован'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserProfileSerializer(user)

            return Response({
                'status': True,
                'message': 'Успешный вход',
                'token': token.key,
                'user': user_serializer.data
            })
        else:
            return Response(
                {'status': False, 'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'status': False, 'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    Выход пользователя (удаление токена).
    """
    try:
        request.user.auth_token.delete()
        return Response({
            'status': True,
            'message': 'Успешный выход'
        })
    except:
        return Response({
            'status': True,
            'message': 'Токен не найден или уже удален'
        })


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Профиль пользователя (просмотр и обновление).
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': 'Профиль обновлен',
                'user': serializer.data
            })
        return Response(
            {'status': False, 'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# ==================== PARTNER UPDATE ====================

import requests
import yaml
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика через YAML (URL или файл).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsShop]  # Только для магазинов
    
    def post(self, request, *args, **kwargs):
        # Получаем магазин пользователя
        try:
            shop = Shop.objects.get(user=request.user)
        except Shop.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Магазин не найден для данного пользователя'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        url = request.data.get('url')
        if url:
            # Валидация URL
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({'Status': False, 'Error': str(e)}, status=400)
            
            # Загрузка данных по URL
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = yaml.safe_load(response.content)
            except requests.RequestException as e:
                return Response({'Status': False, 'Error': f'Ошибка загрузки по URL: {e}'}, status=400)
            except yaml.YAMLError as e:
                return Response({'Status': False, 'Error': f'Ошибка YAML: {e}'}, status=400)
            
            result = self.process_yaml_data(data, shop)
            return Response(result)
        
        # Импорт из загруженного файла
        file = request.FILES.get('file')
        if file:
            try:
                data = yaml.safe_load(file)
                result = self.process_yaml_data(data, shop)
                return Response(result)
            except yaml.YAMLError as e:
                return Response({'Status': False, 'Error': f'Ошибка YAML: {str(e)}'}, status=400)
        
        return Response({'Status': False, 'Error': 'Не указаны данные для импорта'}, status=400)
    
    def process_yaml_data(self, data, shop):
        """Обработка YAML данных (общая логика для URL и файла)"""
        if not data or 'shop' not in data:
            return {'Status': False, 'Error': 'Неверный формат YAML файла'}
        
        categories = data.get('categories', [])
        goods = data.get('goods', [])
        
        # Обновляем название магазина, если изменилось
        if shop.name != data['shop']:
            shop.name = data['shop']
            shop.save()
        
        # Обрабатываем категории
        category_map = {}
        for cat_data in categories:
            category_id = cat_data.get('id')
            category_name = cat_data.get('name')
            
            if not category_id or not category_name:
                continue
            
            category, created = Category.objects.get_or_create(
                id=category_id,
                defaults={'name': category_name}
            )
            category.shops.add(shop)
            category_map[category_id] = category
        
        # Очищаем старые товары магазина
        ProductInfo.objects.filter(shop=shop).delete()
        
        # Обрабатываем товары
        imported_count = 0
        for item in goods:
            try:
                category_id = item.get('category')
                if category_id not in category_map:
                    continue
                
                category = category_map[category_id]
                
                # Создаем или получаем продукт
                product, _ = Product.objects.get_or_create(
                    name=item['name'],
                    category=category
                )
                
                # Создаем информацию о продукте
                product_info = ProductInfo.objects.create(
                    product=product,
                    shop=shop,
                    external_id=item['id'],
                    model=item.get('model', ''),
                    quantity=item['quantity'],
                    price=item['price'],
                    price_rrc=item['price_rrc']
                )
                
                # Обрабатываем параметры
                parameters = item.get('parameters', {})
                for param_name, param_value in parameters.items():
                    param_value_str = str(param_value)
                    parameter, _ = Parameter.objects.get_or_create(name=param_name)
                    ProductParameter.objects.create(
                        product_info=product_info,
                        parameter=parameter,
                        value=param_value_str
                    )
                
                imported_count += 1
                
            except Exception:
                continue
        
        return {
            'Status': True,
            'Message': f'Прайс-лист обновлен. Магазин: {shop.name}',
            'Categories': len(category_map),
            'Products': imported_count
        }

# ==================== КОРЗИНА ====================

from .serializers import BasketItemSerializer, BasketSerializer
from .models import Order, OrderItem

class BasketViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления корзиной покупок.
    """
    serializer_class = BasketItemSerializer
    permission_classes = [IsBuyer]
    
    def get_queryset(self):
        # Получаем или создаем корзину пользователя
        basket, created = Order.objects.get_or_create(
            user=self.request.user,
            status='basket',
            defaults={'status': 'basket'}
        )
        return basket.ordered_items.all()
    
    def get_basket(self):
        """
        Получаем или создаем корзину пользователя.
        """
        basket, created = Order.objects.get_or_create(
            user=self.request.user,
            status='basket',
            defaults={'status': 'basket'}
        )
        return basket
    
    def list(self, request, *args, **kwargs):
        """
        Просмотр корзины с общей стоимостью.
        """
        basket = self.get_basket()
        serializer = BasketSerializer(basket)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Добавление товара в корзину.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        basket = self.get_basket()
        product_info_id = serializer.validated_data['product_info_id']
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Проверяем наличие товара
        try:
            product_info = ProductInfo.objects.get(id=product_info_id)
        except ProductInfo.DoesNotExist:
            return Response(
                {'status': False, 'error': 'Товар не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем достаточно ли товара на складе
        if product_info.quantity < quantity:
            return Response(
                {'status': False, 'error': f'Недостаточно товара на складе. Доступно: {product_info.quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем есть ли уже такой товар в корзине
        order_item, created = OrderItem.objects.get_or_create(
            order=basket,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Если товар уже в корзине, увеличиваем количество
            order_item.quantity += quantity
            # Проверяем не превышает ли новое количество доступное
            if order_item.quantity > product_info.quantity:
                return Response(
                    {'status': False, 'error': f'Недостаточно товара на складе. Доступно: {product_info.quantity}, запрошено: {order_item.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order_item.save()
        
        # Возвращаем созданный/обновленный элемент корзины
        serializer = BasketItemSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Обновление количества товара в корзине.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data.get('quantity', instance.quantity)
        
        # Проверяем достаточно ли товара на складе
        if instance.product_info.quantity < quantity:
            return Response(
                {'status': False, 'error': f'Недостаточно товара на складе. Доступно: {instance.product_info.quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удаление товара из корзины.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'status': True, 'message': 'Товар удален из корзины'},
            status=status.HTTP_200_OK
        )
