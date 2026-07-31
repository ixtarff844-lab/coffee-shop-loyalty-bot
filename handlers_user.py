import os
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.types import InputMediaPhoto
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import database as db
from config import CAFE_INFO
from keyboards import phone_request_kb, main_menu_kb
from states import Registration

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"С возвращением, {message.from_user.first_name}! ☕",
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer(
            "Привет! 👋 Это бот кофейни «Пример».\n\n"
            "Чтобы копить и тратить бонусные баллы, нужно привязать номер телефона. "
            "Нажми кнопку ниже 👇",
            reply_markup=phone_request_kb(),
        )
        await state.set_state(Registration.waiting_for_contact)


@router.message(Registration.waiting_for_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact
    # Разрешаем присылать только свой контакт, не чужой
    if contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправь именно свой номер телефона 🙏")
        return

    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    await db.register_user(
        telegram_id=message.from_user.id,
        phone=phone,
        full_name=message.from_user.full_name,
    )
    await state.clear()
    await message.answer(
        "Готово! Аккаунт привязан ✅\nТеперь тебе доступно меню.",
        reply_markup=main_menu_kb(),
    )


@router.message(Registration.waiting_for_contact)
async def contact_not_sent(message: Message):
    await message.answer(
        "Нужно нажать именно кнопку «Отправить номер телефона» ниже 👇",
        reply_markup=phone_request_kb(),
    )


@router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    photos = [p for p in CAFE_INFO["photos"] if os.path.exists(p)]

    text = (
        f"{CAFE_INFO['description']}\n\n"
        f"📍 Адрес: {CAFE_INFO['address']}\n"
        f"🕒 Часы работы: {CAFE_INFO['hours']}"
    )

    if len(photos) >= 2:
        media = [InputMediaPhoto(media=FSInputFile(p)) for p in photos]
        media[-1].caption = text
        await message.answer_media_group(media)
    elif len(photos) == 1:
        await message.answer_photo(FSInputFile(photos[0]), caption=text)
    else:
        # Фото ещё не загружены в папку photos/ — просто шлём текст
        await message.answer(text)


@router.message(F.text == "📞 Контакты")
async def contacts(message: Message):
    await message.answer(CAFE_INFO["contacts"])


@router.message(F.text == "🎁 Мои баллы")
async def my_points(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала привяжи номер телефона: /start")
        return
    await message.answer(
        f"У тебя на счету: {user['points']:.0f} баллов 🎁\n"
        f"1 балл = 1 ₽ скидки на заказ."
    )

@router.message()
async def fallback(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            "Не понял команду 🤔 Воспользуйся кнопками меню ниже.",
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer("Чтобы начать, нажми /start")