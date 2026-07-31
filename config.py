"""
Конфигурация бота.
Токен получаем у @BotFather в Telegram.
ADMIN_IDS — список telegram_id продавцов/админов, у которых будет доступ
к панели начисления/списания баллов.
"""

import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден. Создай файл .env на основе .env.example "
        "и укажи там свой токен от @BotFather."
    )

# ID можно узнать, например, у бота @userinfobot
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
]

# Сколько баллов начисляем за 1 рубль заказа (например 0.05 = 5% кэшбэк)
POINTS_PER_RUBLE = 0.05

# Сколько рублей стоит 1 балл при списании (обычно 1:1)
RUBLE_PER_POINT = 1.0

# Информация для раздела "О нас"
CAFE_INFO = {
    "description": (
        "☕ Кофейня «Пример»\n\n"
        "Уютное место, где варят лучший кофе в городе. "
        "Свежая выпечка каждое утро, авторские напитки и приятная атмосфера."
    ),
    "address": "г. Москва, ул. Примерная, д. 1",
    "hours": "Пн–Вс: 08:00 – 22:00",
    "contacts": "📞 +7 (900) 000-00-00\n📷 Instagram: @example_coffee\n✈️ Telegram: @example_coffee_manager",
    # Пути к фото кафе — положи файлы в папку photos/ и перечисли тут
    "photos": [
        "photos/cafe_1.jpg",
        "photos/cafe_2.jpg",
    ],
}
