import json
import os
from pathlib import Path

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from dotenv import load_dotenv

from keyboards.inline import confirm_keyboard, team_size_keyboard
from states.registration import RegistrationState

load_dotenv()

GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
APPROVED_CHAT_ID = os.getenv("APPROVED_CHAT_ID")

BASE_DIR = Path(__file__).resolve().parent.parent
PENDING_FILE = BASE_DIR / "pending_reviews.json"
QR_FILE = BASE_DIR / "qr.png"

router = Router()


def ensure_pending_file() -> None