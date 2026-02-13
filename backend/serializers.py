from rest_framework import serializers
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'company',
            'position',
            'type',
            'is_active']
        read_only_fields = ['id', 'is_active']


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'state']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category']
        read_only_fields = ['id']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer(read_only=True)

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = [
            'id',
            'external_id',
            'model',
            'product',
            'shop',
            'quantity',
            'price',
            'price_rrc',
            'product_parameters']
        read_only_fields = ['id']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'city',
            'street',
            'house',
            'structure',
            'building',
            'apartment',
            'phone']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'dt', 'status', 'contact', 'ordered_items']
        read_only_fields = ['id', 'dt']


# ==================== АУТЕНТИФИКАЦИЯ ====================

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'company', 'position', 'type', 'is_active'
        ]
        read_only_fields = ['id', 'email', 'type', 'is_active']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2',
            'first_name', 'last_name', 'company',
            'position', 'type'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            company=validated_data.get('company', ''),
            position=validated_data.get('position', ''),
            type=validated_data.get('type', 'buyer')
        )
        return user


# ==================== КОРЗИНА ====================

class BasketItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)
    product_info_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'product_info_id', 'quantity']
        read_only_fields = ['id']

    def validate_product_info_id(self, value):
        try:
            ProductInfo.objects.get(id=value)
        except ProductInfo.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Количество должно быть положительным")
        return value


class BasketSerializer(serializers.ModelSerializer):
    ordered_items = BasketItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'ordered_items', 'total_price', 'status', 'dt']
        read_only_fields = ['id', 'status', 'dt']

    def get_total_price(self, obj):
        total = 0
        for item in obj.ordered_items.all():
            total += item.quantity * item.product_info.price
        return total
