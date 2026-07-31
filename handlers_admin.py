from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import database as db
from config import ADMIN_IDS, POINTS_PER_RUBLE
from keyboards import admin_menu_kb, main_menu_kb, client_action_kb
from states import AdminFlow

router = Router()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


@router.message(Command("admin"))
async def enter_admin_mode(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа к этому разделу 🚫")
        return
    await message.answer(
        "Режим продавца включён 🧑‍💼\nВведи номер телефона клиента для поиска.",
        reply_markup=admin_menu_kb(),
    )


@router.message(F.text == "⬅️ Выйти из режима админа")
async def exit_admin_mode(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вышли из режима продавца.", reply_markup=main_menu_kb())


@router.message(F.text == "🔍 Найти клиента")
async def ask_phone(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введи номер телефона клиента (в формате +79991234567):")
    await state.set_state(AdminFlow.waiting_for_phone)


@router.message(AdminFlow.waiting_for_phone)
async def find_client(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith("+"):
        phone = "+" + phone

    user = await db.get_user_by_phone(phone)
    if not user:
        await message.answer(
            "Клиент с таким номером не найден ❌\nПроверь номер и попробуй снова, "
            "или нажми «🔍 Найти клиента» ещё раз."
        )
        return

    await state.update_data(client_phone=phone)
    await message.answer(
        f"Клиент найден ✅\n"
        f"Имя: {user['full_name']}\n"
        f"Телефон: {user['phone']}\n"
        f"Баланс баллов: {user['points']:.0f}",
        reply_markup=client_action_kb(),
    )


@router.callback_query(F.data == "accrue")
async def accrue_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"Введи сумму заказа в рублях.\nБаллы начислятся автоматически "
        f"({POINTS_PER_RUBLE * 100:.0f}% от суммы)."
    )
    await state.set_state(AdminFlow.waiting_for_amount_accrue)
    await callback.answer()


@router.message(AdminFlow.waiting_for_amount_accrue)
async def accrue_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("client_phone")

    try:
        amount = float(message.text.replace(",", ".").strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Некорректная сумма. Введи число, например: 350")
        return

    points_delta = round(amount * POINTS_PER_RUBLE, 2)
    new_balance = await db.update_points_by_phone(
        phone=phone, points_delta=points_delta, amount=amount, admin_id=message.from_user.id
    )

    if new_balance is None:
        await message.answer("Ошибка: клиент не найден.")
    else:
        await message.answer(
            f"Начислено {points_delta:.0f} баллов за заказ {amount:.0f} ₽ ✅\n"
            f"Новый баланс клиента: {new_balance:.0f} баллов",
            reply_markup=admin_menu_kb(),
        )
    await state.set_state(None)


@router.callback_query(F.data == "deduct")
async def deduct_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введи количество баллов для списания (например, клиент оплачивает ими часть заказа):"
    )
    await state.set_state(AdminFlow.waiting_for_amount_deduct)
    await callback.answer()


@router.message(AdminFlow.waiting_for_amount_deduct)
async def deduct_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("client_phone")

    try:
        points_to_deduct = float(message.text.replace(",", ".").strip())
        if points_to_deduct <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Некорректное число. Введи количество баллов, например: 100")
        return

    user = await db.get_user_by_phone(phone)
    if not user:
        await message.answer("Ошибка: клиент не найден.")
        await state.clear()
        return

    if points_to_deduct > user["points"]:
        await message.answer(
            f"У клиента недостаточно баллов (доступно: {user['points']:.0f}). "
            f"Введи число меньше или равное балансу."
        )
        return

    new_balance = await db.update_points_by_phone(
        phone=phone, points_delta=-points_to_deduct, amount=None, admin_id=message.from_user.id
    )
    await message.answer(
        f"Списано {points_to_deduct:.0f} баллов ✅\n"
        f"Новый баланс клиента: {new_balance:.0f} баллов",
        reply_markup=admin_menu_kb(),
    )
    await state.set_state(None)
