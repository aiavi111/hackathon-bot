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


TEXTS = {
    "lang_ru": {
        "language_selected": "✅ Язык выбран: Русский",
        "send_team_name": "Теперь отправьте название команды.",
        "team_name_too_short": "Название команды слишком короткое. Попробуйте еще раз.",
        "send_team_name_text": "Пожалуйста, отправьте название команды текстом.",
        "team_name_saved": "✅ Название команды: {team_name}\n\nТеперь выберите количество участников в команде:",
        "team_size_error": "Можно выбрать только от 1 до 6 участников.",
        "solo_intro": "👤 Вы выбрали индивидуальную регистрацию.\n\nВведите ваше имя и фамилию\nПример: Айвар Тынчтыкбеков",
        "team_intro": "👤 Количество участников: {team_size}\n\nВведите имя и фамилию 1 участника\nПример: Айвар Тынчтыкбеков",
        "send_full_name_text": "Пожалуйста, отправьте имя и фамилию текстом.",
        "full_name_error": "Введите имя и фамилию {current} участника одним сообщением.\nПример: Айвар Тынчтыкбеков",
        "send_your_tg": "Теперь отправьте ваш @username или Telegram ID.",
        "send_participant_tg": "Теперь отправьте @username или Telegram ID {current} участника.",
        "send_tg_text": "Пожалуйста, отправьте @username или Telegram ID текстом.",
        "participant_saved": "✅ {current} участник сохранен.\n\nВведите имя и фамилию {next_num} участника\nПример: Айвар Тынчтыкбеков",
        "check_application": "📋 Проверьте данные заявки",
        "language": "🌐 Язык",
        "team": "👥 Команда",
        "participants_count": "👤 Количество участников",
        "members": "Состав",
        "payment_sum": "💰 Сумма к оплате",
        "restart": "🔄 Хорошо, начнем заново.\n\nОтправьте новое название команды.",
        "payment_title": "💳 Оплата регистрации",
        "pay_caption": "👥 Команда: {team_name}\n💰 Сумма к оплате: {total_amount} сом\n\nПожалуйста, оплатите по QR-коду ниже и отправьте чек сюда.\nМожно отправить фото или файл.",
        "qr_not_found": "⚠️ Файл qr.png не найден в папке проекта.",
        "send_receipt_as_file": "Пожалуйста, отправьте чек как фото или как файл.",
        "group_id_missing": "Ошибка: GROUP_CHAT_ID не найден.",
        "new_review": "🧾 Новая заявка на проверку",
        "members_list": "Состав",
        "captain_no_username": "Капитан: без username",
        "reply_confirm": "Чтобы подтвердить оплату, ответьте на это сообщение словом: подтверждено\nЧтобы отклонить, ответьте словом: отклонено",
        "receipt_sent": "✅ Чек отправлен организаторам.\nПосле проверки мы сообщим вам результат.",
        "need_reply": "Нужно ответить на сообщение с чеком словом:\nподтверждено — если оплата прошла\nотклонено — если чек не подходит",
        "review_not_found": "Не нашел заявку для этого сообщения.",
        "already_approved": "Эта заявка уже подтверждена.",
        "solo_success": "✅ Оплата подтверждена.\nВы успешно зарегистрированы на хакатон как индивидуальный участник.\n\nЧтобы найти команду, переходите в чат:\nt.me/vsonujnoe/228",
        "team_success": "✅ Оплата подтверждена.\nВаша команда успешно зарегистрирована на хакатон.",
        "cant_notify_user": "Не получилось отправить сообщение участнику, но заявка будет добавлена в список.",
        "approved_application": "✅ Подтвержденная заявка",
        "paid": "💰 Оплачено",
        "approved_done": "✅ Заявка подтверждена.",
        "rejected_user": "❌ Оплата пока не подтверждена.\nПожалуйста, проверьте чек и отправьте его заново.",
        "rejected_done": "❌ Заявка отклонена. Участнику отправлено сообщение.",
        "cant_notify_rejected": "Не получилось отправить сообщение участнику.",
        "open_profile": "Открыть профиль капитана",
    },
    "lang_kg": {
        "language_selected": "✅ Тил тандалды: Кыргызча",
        "send_team_name": "Эми команданын атын жазыңыз.",
        "team_name_too_short": "Команданын аты өтө кыска. Кайра аракет кылыңыз.",
        "send_team_name_text": "Сураныч, команданын атын текст түрүндө жазыңыз.",
        "team_name_saved": "✅ Команданын аты: {team_name}\n\nЭми катышуучулардын санын тандаңыз:",
        "team_size_error": "1ден 6га чейин гана тандаса болот.",
        "solo_intro": "👤 Сиз жеке катталууну тандадыңыз.\n\nАтыңызды жана фамилияңызды жазыңыз\nМисал: Айвар Тынчтыкбеков",
        "team_intro": "👤 Катышуучулардын саны: {team_size}\n\n1-катышуучунун аты-жөнүн жазыңыз\nМисал: Айвар Тынчтыкбеков",
        "send_full_name_text": "Сураныч, аты-жөнүн текст түрүндө жазыңыз.",
        "full_name_error": "{current}-катышуучунун аты-жөнүн бир билдирүү менен жазыңыз.\nМисал: Айвар Тынчтыкбеков",
        "send_your_tg": "Эми өзүңүздүн @username же Telegram ID жазыңыз.",
        "send_participant_tg": "Эми {current}-катышуучунун @username же Telegram ID жазыңыз.",
        "send_tg_text": "Сураныч, @username же Telegram ID текст түрүндө жазыңыз.",
        "participant_saved": "✅ {current}-катышуучу сакталды.\n\n{next_num}-катышуучунун аты-жөнүн жазыңыз\nМисал: Айвар Тынчтыкбеков",
        "check_application": "📋 Өтүнмөнү текшериңиз",
        "language": "🌐 Тил",
        "team": "👥 Команда",
        "participants_count": "👤 Катышуучулардын саны",
        "members": "Курамы",
        "payment_sum": "💰 Төлөм суммасы",
        "restart": "🔄 Макул, кайра баштайбыз.\n\nЖаңы команданын атын жазыңыз.",
        "payment_title": "💳 Катталуу үчүн төлөм",
        "pay_caption": "👥 Команда: {team_name}\n💰 Төлөм суммасы: {total_amount} сом\n\nQR-код аркылуу төлөп, чекти бул жакка жөнөтүңүз.\nСүрөт же файл түрүндө жөнөтсөңүз болот.",
        "qr_not_found": "⚠️ qr.png файлы долбоор папкасында табылган жок.",
        "send_receipt_as_file": "Сураныч, чекти сүрөт же файл түрүндө жөнөтүңүз.",
        "group_id_missing": "Ката: GROUP_CHAT_ID табылган жок.",
        "new_review": "🧾 Текшерүү үчүн жаңы өтүнмө",
        "members_list": "Курамы",
        "captain_no_username": "Капитан: username жок",
        "reply_confirm": "Төлөмдү ырастоо үчүн ушул билдирүүгө жооп берип: подтверждено деп жазыңыз\nЧекти четке кагуу үчүн: отклонено деп жазыңыз",
        "receipt_sent": "✅ Чек уюштуруучуларга жөнөтүлдү.\nТекшерүүдөн кийин жыйынтыкты билдиребиз.",
        "need_reply": "Чекке жооп кылып төмөнкүлөрдүн бирин жазыңыз:\nподтверждено — төлөм өткөн болсо\nотклонено — чек туура келбесе",
        "review_not_found": "Бул билдирүү үчүн өтүнмө табылган жок.",
        "already_approved": "Бул өтүнмө буга чейин ырасталган.",
        "solo_success": "✅ Төлөм ырасталды.\nСиз хакатонго жеке катышуучу катары ийгиликтүү катталдыңыз.\n\nКоманда табуу үчүн бул чатка өтүңүз:\nt.me/vsonujnoe/228",
        "team_success": "✅ Төлөм ырасталды.\nСиздин команда хакатонго ийгиликтүү катталды.",
        "cant_notify_user": "Катышуучуга билдирүү жөнөтүү мүмкүн болгон жок, бирок өтүнмө тизмеге кошулат.",
        "approved_application": "✅ Ырасталган өтүнмө",
        "paid": "💰 Төлөндү",
        "approved_done": "✅ Өтүнмө ырасталды.",
        "rejected_user": "❌ Төлөм азырынча ырасталган жок.\nСураныч, чекти текшерип кайра жөнөтүңүз.",
        "rejected_done": "❌ Өтүнмө четке кагылды. Катышуучуга билдирүү жөнөтүлдү.",
        "cant_notify_rejected": "Катышуучуга билдирүү жөнөтүү мүмкүн болгон жок.",
        "open_profile": "Капитандын профилин ачуу",
    },
    "lang_en": {
        "language_selected": "✅ Language selected: English",
        "send_team_name": "Now send your team name.",
        "team_name_too_short": "Team name is too short. Try again.",
        "send_team_name_text": "Please send the team name as text.",
        "team_name_saved": "✅ Team name: {team_name}\n\nNow choose the number of participants:",
        "team_size_error": "You can choose only from 1 to 6 participants.",
        "solo_intro": "👤 You selected individual registration.\n\nEnter your full name\nExample: Aivar Tynchtykbekov",
        "team_intro": "👤 Number of participants: {team_size}\n\nEnter full name of participant 1\nExample: Aivar Tynchtykbekov",
        "send_full_name_text": "Please send the full name as text.",
        "full_name_error": "Enter full name of participant {current} in one message.\nExample: Aivar Tynchtykbekov",
        "send_your_tg": "Now send your @username or Telegram ID.",
        "send_participant_tg": "Now send @username or Telegram ID of participant {current}.",
        "send_tg_text": "Please send @username or Telegram ID as text.",
        "participant_saved": "✅ Participant {current} saved.\n\nEnter full name of participant {next_num}\nExample: Aivar Tynchtykbekov",
        "check_application": "📋 Check your application",
        "language": "🌐 Language",
        "team": "👥 Team",
        "participants_count": "👤 Number of participants",
        "members": "Members",
        "payment_sum": "💰 Payment amount",
        "restart": "🔄 Okay, let's start again.\n\nSend a new team name.",
        "payment_title": "💳 Registration payment",
        "pay_caption": "👥 Team: {team_name}\n💰 Payment amount: {total_amount} KGS\n\nPlease pay using the QR code below and send your receipt here.\nYou can send a photo or a file.",
        "qr_not_found": "⚠️ File qr.png was not found in the project folder.",
        "send_receipt_as_file": "Please send the receipt as a photo or a file.",
        "group_id_missing": "Error: GROUP_CHAT_ID not found.",
        "new_review": "🧾 New application for review",
        "members_list": "Members",
        "captain_no_username": "Captain: no username",
        "reply_confirm": "To confirm payment, reply to this message with: подтверждено\nTo reject the receipt, reply with: отклонено",
        "receipt_sent": "✅ Receipt sent to organizers.\nWe will notify you after verification.",
        "need_reply": "Reply to the receipt message with one of these:\nподтверждено — if payment is valid\nотклонено — if receipt is invalid",
        "review_not_found": "No application found for this message.",
        "already_approved": "This application has already been approved.",
        "solo_success": "✅ Payment confirmed.\nYou have been successfully registered for the hackathon as an individual participant.\n\nTo find a team, join this chat:\nt.me/vsonujnoe/228",
        "team_success": "✅ Payment confirmed.\nYour team has been successfully registered for the hackathon.",
        "cant_notify_user": "Could not send a message to the participant, but the application will still be added to the list.",
        "approved_application": "✅ Approved application",
        "paid": "💰 Paid",
        "approved_done": "✅ Application approved.",
        "rejected_user": "❌ Payment has not been confirmed yet.\nPlease check the receipt and send it again.",
        "rejected_done": "❌ Application rejected. The participant has been notified.",
        "cant_notify_rejected": "Could not send a message to the participant.",
        "open_profile": "Open captain profile",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang_dict = TEXTS.get(lang, TEXTS["lang_ru"])
    text = lang_dict.get(key, TEXTS["lang_ru"].get(key, key))
    return text.format(**kwargs)


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
    lang = data.get("language", "lang_ru")
    team_name = data["team_name"]
    team_size = data["team_size"]
    total_amount = data["total_amount"]
    participants = data.get("participants", [])

    text = (
        f"{t(lang, 'check_application')}\n\n"
        f"{t(lang, 'language')}: {get_language_name(lang)}\n"
        f"{t(lang, 'team')}: {team_name}\n"
        f"{t(lang, 'participants_count')}: {team_size}\n\n"
        f"{t(lang, 'members')}:\n"
    )

    for i, p in enumerate(participants, start=1):
        text += f"{i}. {p['full_name']} — {p['telegram']}\n"

    text += f"\n{t(lang, 'payment_sum')}: {total_amount} сом"
    return text


def format_approved_team_text(review_data: dict) -> str:
    lang = review_data.get("language", "lang_ru")
    team_name = review_data["team_name"]
    team_size = review_data["team_size"]
    total_amount = review_data["total_amount"]
    participants = review_data.get("participants", [])

    text = (
        f"{t(lang, 'approved_application')}\n\n"
        f"{t(lang, 'team')}: {team_name}\n"
        f"{t(lang, 'participants_count')}: {team_size}\n"
        f"{t(lang, 'paid')}: {total_amount} сом\n\n"
        f"{t(lang, 'members')}:\n"
    )

    for i, p in enumerate(participants, start=1):
        text += f"{i}. {p['full_name']} — {p['telegram']}\n"

    return text


@router.callback_query(RegistrationState.choosing_language, F.data.startswith("lang_"))
async def language_chosen(callback: CallbackQuery, state: FSMContext):
    lang = callback.data
    await state.update_data(language=lang)
    await state.set_state(RegistrationState.team_name)

    await callback.message.edit_text(
        f"{t(lang, 'language_selected')}\n\n{t(lang, 'send_team_name')}"
    )
    await callback.answer()


@router.message(RegistrationState.team_name)
async def team_name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    if not message.text:
        await message.answer(t(lang, "send_team_name_text"))
        return

    team_name = message.text.strip()

    if len(team_name) < 2:
        await message.answer(t(lang, "team_name_too_short"))
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
        t(lang, "team_name_saved", team_name=team_name),
        reply_markup=team_size_keyboard(),
    )


@router.callback_query(RegistrationState.team_size, F.data.startswith("team_size_"))
async def team_size_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    team_size = int(callback.data.split("_")[-1])

    if team_size < 1 or team_size > 6:
        await callback.answer(t(lang, "team_size_error"))
        return

    await state.update_data(team_size=team_size, current_participant=1)
    await state.set_state(RegistrationState.participant_full_name)

    if team_size == 1:
        text = t(lang, "solo_intro")
    else:
        text = t(lang, "team_intro", team_size=team_size)

    await callback.message.edit_text(text)
    await callback.answer()


@router.message(RegistrationState.participant_full_name)
async def participant_full_name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    if not message.text:
        await message.answer(t(lang, "send_full_name_text"))
        return

    full_name = message.text.strip()
    current = data["current_participant"]

    if len(full_name.split()) < 2:
        await message.answer(t(lang, "full_name_error", current=current))
        return

    await state.update_data(temp_full_name=full_name)
    await state.set_state(RegistrationState.participant_tg)

    if data["team_size"] == 1:
        await message.answer(t(lang, "send_your_tg"))
    else:
        await message.answer(t(lang, "send_participant_tg", current=current))


@router.message(RegistrationState.participant_tg)
async def participant_tg_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    if not message.text:
        await message.answer(t(lang, "send_tg_text"))
        return

    tg_data = message.text.strip()
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
            t(lang, "participant_saved", current=current, next_num=next_num)
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
    lang = data.get("language", "lang_ru")

    await state.clear()
    await state.update_data(language=lang)
    await state.set_state(RegistrationState.team_name)

    await callback.message.edit_text(t(lang, "restart"))
    await callback.answer()


@router.callback_query(RegistrationState.confirm_data, F.data == "confirm_yes")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    total_amount = data["total_amount"]
    team_name = data["team_name"]

    await state.set_state(RegistrationState.waiting_receipt)

    caption = (
        f"{t(lang, 'payment_title')}\n\n"
        f"{t(lang, 'pay_caption', team_name=team_name, total_amount=total_amount)}"
    )

    if QR_FILE.exists():
        photo = FSInputFile(str(QR_FILE))
        await callback.message.answer_photo(photo, caption=caption)
    else:
        await callback.message.answer(
            caption + "\n\n" + t(lang, "qr_not_found")
        )

    await callback.answer()


@router.message(RegistrationState.waiting_receipt, F.photo)
async def receipt_photo_handler(message: Message, state: FSMContext):
    await send_receipt_to_group(message, state, is_photo=True)


@router.message(RegistrationState.waiting_receipt, F.document)
async def receipt_document_handler(message: Message, state: FSMContext):
    await send_receipt_to_group(message, state, is_photo=False)


@router.message(RegistrationState.waiting_receipt)
async def wrong_receipt_format(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")
    await message.answer(t(lang, "send_receipt_as_file"))


async def send_receipt_to_group(message: Message, state: FSMContext, is_photo: bool):
    data = await state.get_data()
    lang = data.get("language", "lang_ru")

    if not GROUP_CHAT_ID:
        await message.answer(t(lang, "group_id_missing"))
        return

    team_name = data["team_name"]
    team_size = data["team_size"]
    total_amount = data["total_amount"]
    captain_username = data.get("captain_username")
    captain_id = data.get("captain_id")
    participants = data.get("participants", [])

    caption = (
        f"{t(lang, 'new_review')}\n\n"
        f"{t(lang, 'team')}: {team_name}\n"
        f"{t(lang, 'participants_count')}: {team_size}\n"
        f"{t(lang, 'payment_sum')}: {total_amount} сом\n\n"
        f"{t(lang, 'members_list')}:\n"
    )

    for i, p in enumerate(participants, start=1):
        caption += f"{i}. {p['full_name']} — {p['telegram']}\n"

    caption += "\n"
    if captain_username:
        caption += f"Капитан: @{captain_username}\n"
    else:
        caption += t(lang, "captain_no_username") + "\n"

    caption += f"Telegram ID капитана: {captain_id}\n"
    caption += f'<a href="tg://user?id={captain_id}">{t(lang, "open_profile")}</a>\n\n'
    caption += t(lang, "reply_confirm")

    group_chat_id = int(GROUP_CHAT_ID)

    if is_photo:
        file_id = message.photo[-1].file_id
        sent_message = await message.bot.send_photo(
            chat_id=group_chat_id,
            photo=file_id,
            caption=caption,
            parse_mode="HTML",
        )
    else:
        file_id = message.document.file_id
        sent_message = await message.bot.send_document(
            chat_id=group_chat_id,
            document=file_id,
            caption=caption,
            parse_mode="HTML",
        )

    pending_reviews = load_pending_reviews()
    pending_reviews[str(sent_message.message_id)] = {
        "captain_id": captain_id,
        "team_name": team_name,
        "team_size": team_size,
        "total_amount": total_amount,
        "participants": participants,
        "status": "pending",
        "language": lang,
    }
    save_pending_reviews(pending_reviews)

    await message.answer(t(lang, "receipt_sent"))
    await state.clear()


@router.message(F.chat.id == int(GROUP_CHAT_ID) if GROUP_CHAT_ID else False)
async def review_by_reply(message: Message):
    if not message.text:
        return

    text = message.text.strip().lower()

    if text not in ["подтверждено", "отклонено", "нет"]:
        return

    if not message.reply_to_message:
        await message.answer(
            "Нужно ответить на сообщение с чеком словом:\n"
            "подтверждено — если оплата прошла\n"
            "отклонено — если чек не подходит"
        )
        return

    replied_message_id = str(message.reply_to_message.message_id)
    pending_reviews = load_pending_reviews()

    if replied_message_id not in pending_reviews:
        await message.answer("Не нашел заявку для этого сообщения.")
        return

    review_data = pending_reviews[replied_message_id]
    lang = review_data.get("language", "lang_ru")

    captain_id = review_data["captain_id"]

    if text == "подтверждено":
        if review_data.get("status") == "approved":
            await message.answer(t(lang, "already_approved"))
            return

        try:
            if review_data["team_size"] == 1:
                user_text = t(lang, "solo_success")
            else:
                user_text = t(lang, "team_success")

            await message.bot.send_message(
                chat_id=captain_id,
                text=user_text,
            )
        except Exception:
            await message.answer(t(lang, "cant_notify_user"))

        if APPROVED_CHAT_ID:
            await message.bot.send_message(
                chat_id=int(APPROVED_CHAT_ID),
                text=format_approved_team_text(review_data),
            )

        review_data["status"] = "approved"
        pending_reviews[replied_message_id] = review_data
        save_pending_reviews(pending_reviews)

        await message.answer(t(lang, "approved_done"))

    elif text in ["отклонено", "нет"]:
        try:
            await message.bot.send_message(
                chat_id=captain_id,
                text=t(lang, "rejected_user"),
            )
        except Exception:
            await message.answer(t(lang, "cant_notify_rejected"))

        review_data["status"] = "rejected"
        pending_reviews[replied_message_id] = review_data
        save_pending_reviews(pending_reviews)

        await message.answer(t(lang, "rejected_done"))