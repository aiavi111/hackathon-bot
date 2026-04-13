from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="Кыргызча", callback_data="lang_kg"),
            ],
            [
                InlineKeyboardButton(text="English", callback_data="lang_en"),
            ]
        ]
    )


def team_size_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="2", callback_data="team_size_2"),
                InlineKeyboardButton(text="3", callback_data="team_size_3"),
            ],
            [
                InlineKeyboardButton(text="4", callback_data="team_size_4"),
                InlineKeyboardButton(text="5", callback_data="team_size_5"),
            ],
            [
                InlineKeyboardButton(text="6", callback_data="team_size_6"),
            ]
        ]
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            ],
            [
                InlineKeyboardButton(text="🔄 Заполнить заново", callback_data="confirm_restart"),
            ]
        ]
    )