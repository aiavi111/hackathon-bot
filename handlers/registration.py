import json
import os
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards.inline import team_size_keyboard, confirm_keyboard
from states.registration import RegistrationState

load_dotenv()

GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
APPROVED_CHAT_ID = os.getenv("APPROVED_CHAT_ID")

BASE_DIR = Path(__file__).resolve().parent.parent
PENDING_FILE = BASE_DIR / "pending_reviews.json"
QR_FILE = BASE_DIR / "qr.png"

router = Router()


def ensure_pending_file():
    if not PENDING_FILE.exists():
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_pending_reviews():
    ensure_pending_file()
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_pending_reviews(data):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_language_name(code: str) -> str:
    languages = {
        "lang_ru": "Русский",
        "lang_kg": "Кыргызча",
        "lang_en": "English",
    }
    return languages.get(code, "Русский")


def format_application_text(data: dict) -> str:
    language_name = get_language_name(data["language"])
    team_name = data["team_name"]
    team_size = data["team_size"]
    total_amount = data["total_amount"]
    participants = data.get("participants", [])

    text = (
        "📋 Проверьте данные заявки\n\n"
        f"🌐 Язык: {language_name}\n"
        f"👥 Команда: {team_name}\n"
        f"👤 Количество участников: {team_size}\n\n"
        "Состав:\n"
    )

    for i, p in enumerate(participants, start=1):
        text += f"{i}. {p['full_name']} — {p['telegram']}\n"

    text += f"\n💰 Сумма к оплате: {total_amount} сом"
    return text


def format_approved_team_text(review_data: dict) -> str:
    team_name = review_data["team_name"]
    team_size = review_data["team_size"]
    total_amount = review_data["total_amount"]
    participants = review_data.get("participants", [])

    text = (
        "✅ Подтвержденная заявка\n\n"
        f"👥 Команда: {team_name}\n"
        f"👤 Количество участников: {team_size}\n"
        f"💰 Оплачено: {total_amount} сом\n\n"
        "Состав:\n"
    )

    for i, p in enumerate(participants, start=1):
        text += f"{i}. {p['full_name']} — {p['telegram']}\n"

    return text


@router.callback_query(RegistrationState.choosing_language, F.data.startswith("lang_"))
async def language_chosen(callback: CallbackQuery, state: FSMContext):
    await state.update_data(language=callback.data)
    await state.set_state(RegistrationState.team_name)

    await callback.message.edit_text(
        f"✅ Язык выбран: {get_language_name(callback.data)}\n\n"
        "Теперь отправьте название команды."
    )
    await callback.answer()


@router.message(RegistrationState.team_name)
async def team_name_handler(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправьте название команды текстом.")
        return

    team_name = message.text.strip()

    if len(team_name) < 2:
        await message.answer("Название команды слишком короткое. Попробуйте еще раз.")
        return

    await state.update_data(
        team_name=team_name,
        captain_id=message.from_user.id,
        captain_username=message.from_user.username,
        participants=[],
        current_participant=1,
    )

    await state.set_state(RegistrationState.team_size)

    await message.answer(
        f"✅ Название команды: {team_name}\n\n"
        "Теперь выберите количество участников в команде:",
        reply_markup=team_size_keyboard(),
    )


@router.callback_query(RegistrationState.team_size, F.data.startswith("team_size_"))
async def team_size_handler(callback: CallbackQuery, state: FSMContext):
    team_size = int(callback.data.split("_")[-1])

    if team_size < 1 or team_size > 6:
        await callback.answer("Можно выбрать только от 1 до 6 участников.")
        return

    await state.update_data(team_size=team_size, current_participant=1)
    await state.set_state(RegistrationState.participant_full_name)

    if team_size == 1:
        text = (
            "👤 Вы выбрали индивидуальную регистрацию.\n\n"
            "Введите ваше имя и фамилию\n"
            "Пример: Айвар Тынчтыкбеков"
        )
    else:
        text = (
            f"👤 Количество участников: {team_size}\n\n"
            "Введите имя и фамилию 1 участника\n"
            "Пример: Айвар Тынчтыкбеков"
        )

    await callback.message.edit_text(text)
    await callback.answer()


@router.message(RegistrationState.participant_full_name)
async def participant_full_name_handler(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправьте имя и фамилию текстом.")
        return

    full_name = message.text.strip()
    data = await state.get_data()
    current = data["current_participant"]

    if len(full_name.split()) < 2:
        await message.answer(
            f"Введите имя и фамилию {current} участника одним сообщением.\n"
            "Пример: Айвар Тынчтыкбеков"
        )
        return

    await state.update_data(temp_full_name=full_name)
    await state.set_state(RegistrationState.participant_tg)

    if data["team_size"] == 1:
        await message.answer("Теперь отправьте ваш @username или Telegram ID.")
    else:
        await message.answer(
            f"Теперь отправьте @username или Telegram ID {current} участника."
        )


@router.message(RegistrationState.participant_tg)
async def participant_tg_handler(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправьте @username или Telegram ID текстом.")
        return

    tg_data = message.text.strip()
    data = await state.get_data()

    participants = data.get("participants", [])
    current = data["current_participant"]
    team_size = data["team_size"]

    participant = {
        "full_name": data["temp_full_name"],
        "telegram": tg_data,
    }
    participants.append(participant)

    await state.update_data(participants=participants)

    if current < team_size:
        next_num = current + 1
        await state.update_data(current_participant=next_num)
        await state.set_state(RegistrationState.participant_full_name)

        await message.answer(
            f"✅ {current} участник сохранен.\n\n"
            f"Введите имя и фамилию {next_num} участника\n"
            "Пример: Айвар Тынчтыкбеков"
        )
        return

    total_amount = team_size * 200
    await state.update_data(total_amount=total_amount)
    await state.set_state(RegistrationState.confirm_data)

    final_data = await state.get_data()
    await message.answer(
        format_application_text(final_data),
        reply_markup=confirm_keyboard(),
    )


@router.callback_query(RegistrationState.confirm_data, F.data == "confirm_restart")
async def restart_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")

    await state.clear()
    await state.update_data(language=language)
    await state.set_state(RegistrationState.team_name)

    await callback.message.edit_text(
        "🔄 Хорошо, начнем заново.\n\n"
        "Отправьте новое название команды."
    )
    await callback.answer()


@router.callback_query(RegistrationState.confirm_data, F.data == "confirm_yes")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_amount = data["total_amount"]
    team_name = data["team_name"]

    await state.set_state(RegistrationState.waiting_receipt)

    caption = (
        "💳 Оплата регистрации\n\n"
        f"👥 Команда: {team_name}\n"
        f"💰 Сумма к оплате: {total_amount} сом\n\n"
        "Пожалуйста, оплатите по QR-коду ниже и отправьте чек сюда.\n"
        "Можно отправить фото или файл."
    )

    if QR_FILE.exists():
        photo = FSInputFile(str(QR_FILE))
        await callback.message.answer_photo(photo, caption=caption)
    else:
        await callback.message.answer(
            caption + "\n\n⚠️ Файл qr.png не найден в папке проекта."
        )

    await callback.answer()


@router.message(RegistrationState.waiting_receipt, F.photo)
async def receipt_photo_handler(message: Message, state: FSMContext):
    await send_receipt_to_group(message, state, is_photo=True)


@router.message(RegistrationState.waiting_receipt, F.document)
async def receipt_document_handler(message: Message, state: FSMContext):
    await send_receipt_to_group(message, state, is_photo=False)


@router.message(RegistrationState.waiting_receipt)
async def wrong_receipt_format(message: Message):
    await message.answer("Пожалуйста, отправьте чек как фото или как файл.")


async def send_receipt_to_group(message: Message, state: FSMContext, is_photo: bool):
    if not GROUP_CHAT_ID:
        await message.answer("Ошибка: GROUP_CHAT_ID не найден.")
        return

    data = await state.get_data()

    team_name = data["team_name"]
    team_size = data["team_size"]
    total_amount = data["total_amount"]
    captain_username = data.get("captain_username")
    captain_id = data.get("captain_id")
    participants = data.get("participants", [])

    caption = (
        "🧾 Новая заявка на проверку\n\n"
        f"👥 Команда: {team_name}\n"
        f"👤 Участников: {team_size}\n"
        f"💰 Сумма: {total_amount} сом\n\n"
        "Состав:\n"
    )

    for i, p in enumerate(participants, start=1):
        caption += f"{i}. {p['full_name']} — {p['telegram']}\n"

    caption += "\n"
    if captain_username:
        caption += f"Капитан: @{captain_username}\n"
    else:
        caption += "Капитан: без username\n"

    caption += f"Telegram ID капитана: {captain_id}\n\n"
    caption += "Чтобы подтвердить оплату, ответьте на это сообщение словом: подтверждено"

    group_chat_id = int(GROUP_CHAT_ID)

    if is_photo:
        file_id = message.photo[-1].file_id
        sent_message = await message.bot.send_photo(
            chat_id=group_chat_id,
            photo=file_id,
            caption=caption,
        )
    else:
        file_id = message.document.file_id
        sent_message = await message.bot.send_document(
            chat_id=group_chat_id,
            document=file_id,
            caption=caption,
        )

    pending_reviews = load_pending_reviews()
    pending_reviews[str(sent_message.message_id)] = {
        "captain_id": captain_id,
        "team_name": team_name,
        "team_size": team_size,
        "total_amount": total_amount,
        "participants": participants,
        "status": "pending",
    }
    save_pending_reviews(pending_reviews)

    await message.answer(
        "✅ Чек отправлен организаторам.\n"
        "После проверки мы сообщим вам результат."
    )

    await state.clear()


@router.message(F.chat.id == int(GROUP_CHAT_ID) if GROUP_CHAT_ID else False)
async def approve_by_reply(message: Message):
    if not message.text:
        return

    if message.text.strip().lower() != "подтверждено":
        return

    if not message.reply_to_message:
        await message.answer("Нужно ответить словом 'подтверждено' именно на сообщение с чеком.")
        return

    replied_message_id = str(message.reply_to_message.message_id)
    pending_reviews = load_pending_reviews()

    if replied_message_id not in pending_reviews:
        await message.answer("Не нашел заявку для этого сообщения.")
        return

    review_data = pending_reviews[replied_message_id]

    if review_data.get("status") == "approved":
        await message.answer("Эта заявка уже подтверждена.")
        return

    captain_id = review_data["captain_id"]

    try:
        if review_data["team_size"] == 1:
            user_text = (
                "✅ Оплата подтверждена.\n"
                "Вы успешно зарегистрированы на хакатон как индивидуальный участник.\n\n"
                "Чтобы найти команду, переходите в чат:\n"
                "t.me/vsonujnoe/228"
            )
        else:
            user_text = (
                "✅ Оплата подтверждена.\n"
                "Ваша команда успешно зарегистрирована на хакатон."
            )

        await message.bot.send_message(
            chat_id=captain_id,
            text=user_text,
        )
    except Exception:
        await message.answer(
            "Не получилось отправить сообщение участнику, но заявка будет добавлена в список."
        )

    if APPROVED_CHAT_ID:
        await message.bot.send_message(
            chat_id=int(APPROVED_CHAT_ID),
            text=format_approved_team_text(review_data),
        )

    review_data["status"] = "approved"
    pending_reviews[replied_message_id] = review_data
    save_pending_reviews(pending_reviews)

    await message.answer(
        "✅ Команда подтверждена. Участнику отправлено сообщение, состав добавлен в список."
    )