from django.core.management.base import BaseCommand
from backend.import_logic import YamlImporter


class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла (локального или по URL)'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str, help='Путь к YAML файлу или URL')

    def handle(self, *args, **options):
        source = options['source']

        try:
            data = YamlImporter.load_yaml(source)
            result = YamlImporter.process_data(data)

            self.stdout.write(self.style.SUCCESS(
                f'✅ Импорт завершен успешно!\n'
                f'   Магазин: {result["shop"].name}\n'
                f'   Категорий: {result["categories"]}\n'
                f'   Товаров: {result["products"]}'
            ))

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка импорта: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Неизвестная ошибка: {e}'))