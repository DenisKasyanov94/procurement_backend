import yaml
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class YamlImporter:
    """
    Общий класс для импорта данных из YAML.
    Используется как в команде import_data, так и в PartnerUpdate API.
    """

    @staticmethod
    def load_yaml(source):
        """
        Загрузка YAML из файла или URL.

        Args:
            source: Путь к файлу или URL

        Returns:
            dict: Данные из YAML

        Raises:
            ValueError: Если источник недоступен или невалидный
        """
        if source.startswith(('http://', 'https://')):
            try:
                response = requests.get(source, timeout=10)
                response.raise_for_status()
                return yaml.safe_load(response.content)
            except requests.RequestException as e:
                raise ValueError(f'Ошибка загрузки по URL: {e}')
        else:
            try:
                with open(source, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            except FileNotFoundError:
                raise ValueError(f'Файл не найден: {source}')
            except yaml.YAMLError as e:
                raise ValueError(f'Ошибка YAML: {e}')

    @staticmethod
    def process_data(data, shop=None):
        """
        Основная логика обработки YAML данных.

        Args:
            data: Данные из YAML
            shop: Существующий магазин (для PartnerUpdate) или None

        Returns:
            dict: Результат импорта
        """
        if not data or 'shop' not in data:
            raise ValueError('Неверный формат YAML файла')

        shop_name = data['shop']
        categories = data.get('categories', [])
        goods = data.get('goods', [])

        # Создаем или получаем магазин
        if shop:
            # Обновляем существующий магазин
            if shop.name != shop_name:
                shop.name = shop_name
                shop.save()
        else:
            shop, _ = Shop.objects.get_or_create(
                name=shop_name,
                defaults={'state': True}
            )

        # Обрабатываем категории
        category_map = {}
        for cat_data in categories:
            category_id = cat_data.get('id')
            category_name = cat_data.get('name')

            if not category_id or not category_name:
                continue

            category, _ = Category.objects.get_or_create(
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

            except Exception as e:
                print(f"Ошибка обработки товара {item.get('id')}: {e}")
                continue

        return {
            'shop': shop,
            'categories': len(category_map),
            'products': imported_count
        }