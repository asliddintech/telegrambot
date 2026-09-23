from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional
from config import MAIN_CHANNEL, MAIN_CHANNEL_URL
from utils.checker import clean_channel_username

def creator_sub_check_keyboard() -> InlineKeyboardMarkup:
    """Konkurs yaratuvchi uchun kanalga obunani tekshirish tugmasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Homiy kanal: Developer Asliddin",
                    url=MAIN_CHANNEL_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Obunani tekshirish",
                    callback_data="verify_creator_sub"
                )
            ]
        ]
    )

def contest_join_keyboard(contest_id: int, required_channel: Optional[str]) -> InlineKeyboardMarkup:
    """Konkursda ishtirok etish va obuna tugmalari"""
    buttons = []

    # 1. Bosh majburiy kanal (@developer_asliddin)
    buttons.append([
        InlineKeyboardButton(
            text="📢 1-Kanal: Developer Asliddin",
            url=MAIN_CHANNEL_URL
        )
    ])

    # 2. Qo'shimcha kanal (agar mavjud bo'lsa)
    if required_channel:
        clean_ch = clean_channel_username(required_channel)
        ch_name = clean_ch.replace("@", "")
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 2-Kanal: {clean_ch}",
                url=f"https://t.me/{ch_name}"
            )
        ])

    # 3. Tekshirish va Qatnashish tugmasi
    buttons.append([
        InlineKeyboardButton(
            text="✅ Obunani tekshirish / Qatnashish",
            callback_data=f"check_sub_{contest_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def contest_manage_keyboard(contest_id: int, status: str, can_spin: bool) -> InlineKeyboardMarkup:
    """Konkurs egasi boshqaruv paneli tugmalari"""
    buttons = []

    if status == 'active':
        if can_spin:
            buttons.append([
                InlineKeyboardButton(
                    text="🎰 Barabanni aylantirish (30s)",
                    callback_data=f"spin_contest_{contest_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text="⚡️ Barabanni muddatdan oldin aylantirish",
                    callback_data=f"spin_contest_{contest_id}"
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                text="🔗 Havolani olish",
                callback_data=f"share_link_{contest_id}"
            ),
            InlineKeyboardButton(
                text="👥 Ishtirokchilar",
                callback_data=f"view_parts_{contest_id}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="🛑 Konkursni yakunlash",
                callback_data=f"end_confirm_{contest_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="🏆 G'oliblarni ko'rish",
                callback_data=f"view_winners_{contest_id}"
            ),
            InlineKeyboardButton(
                text="👥 Ishtirokchilar",
                callback_data=f"view_parts_{contest_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="◀️ Ortga", callback_data="my_contests_list")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def end_confirm_keyboard(contest_id: int) -> InlineKeyboardMarkup:
    """Konkursni yakunlashni tasdiqlash"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔴 Ha, konkursni yakunlash",
                    callback_data=f"do_end_{contest_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"manage_contest_{contest_id}"
                )
            ]
        ]
    )

def custom_wheel_keyboard() -> InlineKeyboardMarkup:
    """Mustaqil baraban inline tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎡 Barabanni aylantirish (30s)",
                    callback_data="spin_custom_wheel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Nomlarni yangilash",
                    callback_data="restart_custom_wheel"
                )
            ]
        ]
    )
