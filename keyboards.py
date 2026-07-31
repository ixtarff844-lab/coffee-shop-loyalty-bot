from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Клавиатура запроса номера телефона (только при первом старте)
def phone_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# Главное меню для обычного пользователя
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ О нас"), KeyboardButton(text="📞 Контакты")],
            [KeyboardButton(text="🎁 Мои баллы")],
        ],
        resize_keyboard=True,
    )


# Меню для администратора/продавца
def admin_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти клиента")],
            [KeyboardButton(text="⬅️ Выйти из режима админа")],
        ],
        resize_keyboard=True,
    )


# Инлайн-кнопки действий с найденным клиентом (продавцу)
def client_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Начислить баллы", callback_data="accrue"),
                InlineKeyboardButton(text="➖ Списать баллы", callback_data="deduct"),
            ]
        ]
    )
