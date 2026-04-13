from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.inline import language_keyboard
from states.registration import RegistrationState

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegistrationState.choosing_language)

    text = (
        "👋 Добро пожаловать в бот регистрации на хакатон!\n\n"
        "Здесь вы сможете:\n"
        "• зарегистрировать команду\n"
        "• указать участников\n"
        "• получить QR для оплаты\n"
        "• отправить чек организаторам\n\n"
        "Выберите язык:"
    )

    await message.answer(text, reply_markup=language_keyboard())