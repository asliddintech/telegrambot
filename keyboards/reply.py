from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Neon uslubidagi asosiy menyu tugmalari"""
    kb = [
        [
            KeyboardButton(text="⚡️ Yangi Konkurs yaratish"),
            KeyboardButton(text="📋 Mening Konkurslarim")
        ],
        [
            KeyboardButton(text="🎰 Random Baraban"),
            KeyboardButton(text="ℹ️ Bot haqida")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="🌌 Kerakli bo'limni tanlang..."
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    kb = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def skip_or_cancel_keyboard() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish yoki bekor qilish tugmasi"""
    kb = [
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
