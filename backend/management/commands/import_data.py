import yaml
import requests
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла (локального или по URL)'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str, help='Путь к YAML файлу или URL')

    def handle(self, *args, **options):
        source = options['source']

        # Определяем источник данных
        if source.startswith('http://') or source.startswith('https://'):
            # Загрузка по URL
            self.stdout.write(f'Загрузка данных по URL: {source}')
            try:
                response = requests.get(source, timeout=10)
                response.raise_for_status()
                data = yaml.safe_load(response.content)
                self.stdout.write(self.style.SUCCESS(f'Данные загружены по URL'))
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Ошибка загрузки по URL: {e}'))
                return
        else:
            # Загрузка из локального файла
            self.stdout.write(f'Загрузка данных из файла: {source}')
            try:
                with open(source, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                self.stdout.write(self.style.SUCCESS(f'Данные загружены из файла'))
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'Файл не найден: {source}'))
                return
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f'Ошибка YAML: {e}'))
                return

        # Проверяем структуру данных
        if not data or 'shop' not in data:
            self.stdout.write(self.style.ERROR('Неверный формат YAML файла'))
            return

        self.import_data(data)

    def import_data(self, data):
        shop_name = data['shop']
        categories = data.get('categories', [])
        goods = data.get('goods', [])

        # Создаем или получаем магазин
        shop, created = Shop.objects.get_or_create(
            name=shop_name,
            defaults={'state': True}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан магазин: {shop_name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Магазин уже существует: {shop_name}'))
            # Очищаем старые данные магазина
            deleted_count, _ = ProductInfo.objects.filter(shop=shop).delete()
            if deleted_count:
                self.stdout.write(self.style.WARNING(f'Удалено {deleted_count} старых записей товаров'))

        # Обрабатываем категории
        category_map = {}
        for cat_data in categories:
            category_id = cat_data.get('id')
            category_name = cat_data.get('name')

            if not category_id or not category_name:
                self.stdout.write(self.style.WARNING(f'Пропущена категория с неполными данными: {cat_data}'))
                continue

            category, created = Category.objects.get_or_create(
                id=category_id,
                defaults={'name': category_name}
            )
            category.shops.add(shop)
            category_map[category_id] = category

            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {category_name} (ID: {category_id})'))
            else:
                # Обновляем название категории, если изменилось
                if category.name != category_name:
                    category.name = category_name
                    category.save()
                    self.stdout.write(self.style.WARNING(f'Обновлена категория: {category_name}'))

        # Обрабатываем товары
        imported_count = 0
        for item in goods:
            try:
                category_id = item.get('category')
                if category_id not in category_map:
                    self.stdout.write(self.style.WARNING(f'Пропущен товар: категория {category_id} не найдена'))
                    continue

                category = category_map[category_id]

                # Создаем или получаем продукт
                product, created = Product.objects.get_or_create(
                    name=item['name'],
                    category=category
                )

                # Создаем информацию о продукте
                product_info, created = ProductInfo.objects.get_or_create(
                    product=product,
                    shop=shop,
                    external_id=item['id'],
                    defaults={
                        'model': item.get('model', ''),
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'price_rrc': item['price_rrc']
                    }
                )

                # Если запись уже существует, обновляем данные
                if not created:
                    product_info.model = item.get('model', '')
                    product_info.quantity = item['quantity']
                    product_info.price = item['price']
                    product_info.price_rrc = item['price_rrc']
                    product_info.save()

                # Обрабатываем параметры
                parameters = item.get('parameters', {})
                for param_name, param_value in parameters.items():
                    # Преобразуем значение в строку
                    param_value_str = str(param_value)

                    # Создаем или получаем параметр
                    parameter, _ = Parameter.objects.get_or_create(name=param_name)

                    # Создаем или обновляем связь параметра с продуктом
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': param_value_str}
                    )

                imported_count += 1
                self.stdout.write(self.style.SUCCESS(f'Обработан товар: {item["name"]}'))

            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'Ошибка в данных товара: отсутствует поле {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка обработки товара: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'Импорт завершен. Магазин: {shop_name}, '
            f'Категорий: {len(category_map)}, '
            f'Товаров: {imported_count}/{len(goods)}'
        ))