import logging
import re
from typing import Tuple, Optional
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logger = logging.getLogger(__name__)

def clean_channel_username(channel_str: str) -> str:
    """Havola yoki @usernameni toza @username ko'rinishiga keltiradi"""
    channel_str = channel_str.strip()
    # https://t.me/channel_name yoki t.me/channel_name
    match = re.search(r'(?:https?://)?(?:t\.me/|telegram\.me/)?@?([a-zA-Z0-9_]{4,})', channel_str)
    if match:
        return f"@{match.group(1)}"
    if not channel_str.startswith("@") and not channel_str.startswith("-100"):
        return f"@{channel_str}"
    return channel_str

async def check_subscription(bot: Bot, chat_id: str, user_id: int) -> Tuple[bool, Optional[str]]:
    """
    Foydalanuvchining kanalga a'zo ekanligini tekshiradi.
    (status: bool, error_message: Optional[str])
    """
    cleaned_chat = clean_channel_username(chat_id)
    try:
        member = await bot.get_chat_member(chat_id=cleaned_chat, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True, None
        return False, None
    except TelegramBadRequest as e:
        logger.warning(f"Obuna tekshirishda xatolik ({cleaned_chat}): {e}")
        # Agar bot kanal a'zosi bo'lmasa yoki kanal topilmasa
        if "chat not found" in str(e).lower():
            return False, f"⚠️ Kanal topilmadi ({cleaned_chat}). Manzil to'g'riligini tekshiring."
        elif "bot is not a member" in str(e).lower() or "member list is inaccessible" in str(e).lower():
            # Agar bot kanalda admin bo'lmasa
            return False, f"⚠️ Bot {cleaned_chat} kanalida admin emas. Obunani tekshirish uchun botni kanalingizga admin qilib qo'shishingiz kerak."
        return False, None
    except TelegramForbiddenError:
        return False, f"⚠️ Bot {cleaned_chat} kanaliga kira olmadi. Botni kanalga admin qilib qo'shing."
    except Exception as e:
        logger.error(f"Kutilmagan xatolik obunada: {e}")
        return False, None
