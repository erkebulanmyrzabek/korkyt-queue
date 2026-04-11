from aiogram.fsm.state import State, StatesGroup


class QueueRegistration(StatesGroup):
    waiting_for_iin = State()
    waiting_for_photo = State()

