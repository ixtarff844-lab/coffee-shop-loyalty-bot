from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_for_contact = State()


class AdminFlow(StatesGroup):
    waiting_for_phone = State()      # админ вводит номер клиента для поиска
    waiting_for_amount_accrue = State()  # сумма заказа для начисления
    waiting_for_amount_deduct = State()  # сумма/кол-во баллов для списания
