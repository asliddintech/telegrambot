import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
MAIN_CHANNEL: str = os.getenv("MAIN_CHANNEL", "@developer_asliddin")
MAIN_CHANNEL_URL: str = os.getenv("MAIN_CHANNEL_URL", "https://t.me/developer_asliddin")
DB_PATH: str = os.getenv("DB_PATH", "bot.db")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN aniqlanmadi! Iltimos .env faylini tekshiring.")
