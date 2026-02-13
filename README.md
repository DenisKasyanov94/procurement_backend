# Backend-приложение для автоматизации закупок

Дипломный проект профессии «Python-разработчик: расширенный курс»

## Описание проекта

REST API сервис для автоматизации закупок в розничной сети. 
Позволяет покупателям делать заказы у разных поставщиков, а поставщикам - управлять своими прайс-листами.

## Функциональность

- Регистрация и аутентификация пользователей (покупатели и магазины)
- Управление контактами доставки
- Просмотр каталога товаров с фильтрацией и поиском
- Корзина покупок (добавление, просмотр, обновление, удаление)
- Оформление заказов с выбором адреса доставки
- История заказов
- Импорт товаров из YAML файлов (локальных или по URL)
- API для обновления прайс-листов магазинов
- Отправка email уведомлений (подтверждение регистрации, подтверждение заказа)

## Технологии

- Python 3.10+
- Django 5.2
- Django REST Framework
- PostgreSQL
- Token Authentication
- PyYAML для импорта данных
- SMTP для email уведомлений (консольный вывод в разработке)

## Структура проекта

procurement_backend/
├── backend/ # Основное приложение
│ ├── management/ # Кастомные команды
│ │ └── commands/ # Команда import_data
│ ├── migrations/ # Миграции БД
│ ├── templates/ # HTML шаблоны для email
│ │ └── emails/ # Шаблоны писем
│ ├── utils/ # Вспомогательные модули
│ │ └── email_utils.py # Функции отправки email
│ ├── admin.py # Настройки админки
│ ├── import_logic.py # Общая логика импорта YAML
│ ├── models.py # Модели данных (11 моделей)
│ ├── permissions.py # Кастомные permissions
│ ├── serializers.py # Сериализаторы DRF
│ ├── urls.py # Маршруты API
│ └── views.py # Контроллеры (ViewSet'ы и APIView)
├── procurement_backend/ # Настройки проекта
│ ├── settings.py # Основные настройки
│ └── urls.py # Корневые маршруты
├── data/ # Тестовые YAML файлы
│ └── shop1.yaml # Данные магазина "Связной"
├── .env # Переменные окружения (не в git)
├── .gitignore # Игнорируемые файлы
├── manage.py # Управление Django
└── requirements.txt # Зависимости проекта

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/DenisKasyanov94/procurement_backend.git
cd procurement_backend

2. Создание виртуального окружения

python3 -m venv env
source env/bin/activate  # для Linux/Mac
# или
env\Scripts\activate  # для Windows

3. Установка зависимостей

pip install -r requirements.txt

4. Настройка базы данных (PostgreSQL)

CREATE USER diplom_user WITH PASSWORD 'your_password';
CREATE DATABASE procurement_db OWNER diplom_user;

5. Настройка переменных окружения

Создайте файл .env в корне проекта:

DB_NAME=procurement_db
DB_USER=diplom_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Для разработки email выводится в консоль
# Для продакшена раскомментируйте и настройте:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

6. Применение миграций

python manage.py makemigrations
python manage.py migrate

7. Создание суперпользователя

python manage.py createsuperuser

8. Импорт тестовых данных

# Импорт из локального файла
python manage.py import_data data/shop1.yaml

# Или импорт по URL
python manage.py import_data
 "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"

9. Запуск сервера

python manage.py runserver

Сервер будет доступен по адресу: http://127.0.0.1:8000/


Тестовые данные

После импорта в системе доступны:

Магазин:

    "Связной" (ID: 1)

Категории:

    Смартфоны (ID: 224)

    Аксессуары (ID: 15)

    Flash-накопители (ID: 1)

    Телевизоры (ID: 5)

Товары: 14 позиций, включая iPhone, Samsung, телевизоры и флешки

Тестовые пользователи:
Роль	Email	Пароль
Покупатель	buyer@example.com	buyer123
Магазин	shop@example.com	shop123
Администратор	создается командой createsuperuser

API Endpoints
Аутентификация
Метод	Endpoint	Описание
POST	/api/v1/user/register/	Регистрация нового пользователя
POST	/api/v1/user/login/	Вход (получение токена)
POST	/api/v1/user/logout/	Выход (удаление токена)
GET/PUT	/api/v1/user/profile/	Просмотр и обновление профиля

Каталог
Метод	Endpoint	Описание
GET	/api/v1/shops/	Список магазинов
GET	/api/v1/categories/	Категории товаров
GET	/api/v1/products/	Список товаров
GET	/api/v1/product-info/	Информация о товарах (цены, параметры, наличие)

Контакты доставки
Метод	Endpoint	Описание
GET	/api/v1/contacts/	Список контактов
POST	/api/v1/contacts/	Создание контакта
PUT	/api/v1/contacts/{id}/	Обновление контакта
DELETE	/api/v1/contacts/{id}/	Удаление контакта

Корзина
Метод	Endpoint	Описание
GET	/api/v1/basket/	Просмотр корзины
POST	/api/v1/basket/	Добавление товара в корзину
PUT	/api/v1/basket/{id}/	Обновление количества товара
DELETE	/api/v1/basket/{id}/	Удаление товара из корзины

Заказы
Метод	Endpoint	Описание
GET	/api/v1/orders/	История заказов
GET	/api/v1/orders/{id}/	Детали заказа
POST	/api/v1/order/confirm/	Оформление заказа из корзины

Для магазинов
Метод	Endpoint	Описание
POST	/api/v1/partner/update/	Обновление прайс-листа (URL или файл)

                            """Примеры запросов"""
                        
1. Регистрация нового пользователя

curl -X POST http://127.0.0.1:8000/api/v1/user/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "password2": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "type": "buyer"
  }'

2. Вход и получение токена

curl -X POST http://127.0.0.1:8000/api/v1/user/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "buyer@example.com", "password": "buyer123"}'

3. Добавление товара в корзину

curl -X POST http://127.0.0.1:8000/api/v1/basket/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"product_info_id": 15, "quantity": 2}'

4. Просмотр корзины

curl -X GET http://127.0.0.1:8000/api/v1/basket/ \
  -H "Authorization: Token YOUR_TOKEN"

5. Создание контакта доставки

curl -X POST http://127.0.0.1:8000/api/v1/contacts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "city": "Москва",
    "street": "Тверская",
    "house": "1",
    "phone": "+79991234567"
  }'

6. Оформление заказа

curl -X POST http://127.0.0.1:8000/api/v1/order/confirm/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"contact_id": 3}'

7. Обновление прайс-листа магазина

curl -X POST http://127.0.0.1:8000/api/v1/partner/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SHOP_TOKEN" \
  -d '{"url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"}'

8. Просмотр истории заказов

curl -X GET http://127.0.0.1:8000/api/v1/orders/ \
  -H "Authorization: Token YOUR_TOKEN"
  

                        """Email уведомления"""

В режиме разработки email выводятся в консоль (не отправляются реально). Это позволяет отлаживать без настройки SMTP.

Какие письма отправляются:
Тип	Кому	Когда
Подтверждение регистрации	Пользователь	После успешной регистрации
Подтверждение заказа	Покупатель	После оформления заказа
Уведомление о новом заказе	Администратор	После оформления заказа

                        """Разработчик"""

Денис Касьянов
GitHub: DenisKasyanov94