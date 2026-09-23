from aiogram.fsm.state import State, StatesGroup

class ContestCreation(StatesGroup):
    title = State()
    description = State()
    channel = State()
    target_count = State()

class CustomWheel(StatesGroup):
    waiting_for_items = State()
