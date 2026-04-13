from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    choosing_language = State()
    team_name = State()
    team_size = State()
    participant_full_name = State()
    participant_tg = State()
    confirm_data = State()
    waiting_receipt = State()