from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    selecting_plan = State()
    confirming_order = State()
    awaiting_payment = State()
