import asyncio
import logging
import random
from typing import List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

from config import MAIN_CHANNEL
from database.db import db
from keyboards.inline import contest_manage_keyboard, end_confirm_keyboard
from utils.checker import check_subscription
from utils.neon_ui import (
    format_contest_card,
    format_winners_podium,
    generate_drum_frame,
    progress_bar
)

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "📋 Mening Konkurslarim")
async def my_contests(message: Message):
    user_id = message.from_user.id
    contests = await db.get_user_contests(user_id)

    if not contests:
        await message.answer(
            "📭 <b>Sizda hali yaratilgan konkurslar yo'q.</b>\n\n"
            "Yangi konkurs yaratish uchun pastdagi <b>'⚡️ Yangi Konkurs yaratish'</b> tugmasini bosing!",
            parse_mode="HTML"
        )
        return

    buttons = []
    for c in contests:
        status_icon = "🟢" if c['status'] == 'active' else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} #{c['id']} - {c['title']}",
                callback_data=f"manage_contest_{c['id']}"
            )
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        "⚡️ <b>SIZNING KONKURSLARINGIZ RO'YXATI:</b> ⚡️\n<i>Boshqarish uchun tanlang:</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_contests_list")
async def cb_my_contests(callback: CallbackQuery):
    user_id = callback.from_user.id
    contests = await db.get_user_contests(user_id)

    if not contests:
        await callback.message.edit_text("📭 Sizda hozircha konkurslar mavjud emas.")
        return

    buttons = []
    for c in contests:
        status_icon = "🟢" if c['status'] == 'active' else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} #{c['id']} - {c['title']}",
                callback_data=f"manage_contest_{c['id']}"
            )
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "⚡️ <b>SIZNING KONKURSLARINGIZ RO'YXATI:</b> ⚡️\n<i>Boshqarish uchun tanlang:</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("manage_contest_"))
async def cb_manage_contest(callback: CallbackQuery, bot: Bot):
    contest_id = int(callback.data.replace("manage_contest_", ""))
    contest = await db.get_contest(contest_id)

    if not contest:
        await callback.answer("❌ Konkurs topilmadi!", show_alert=True)
        return

    parts_count = await db.get_participants_count(contest_id)
    bot_info = await bot.get_me()
    can_spin = parts_count >= contest['target_count']

    card = format_contest_card(contest, parts_count, bot_info.username)
    kb = contest_manage_keyboard(contest_id, contest['status'], can_spin)

    await callback.message.edit_text(card, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("share_link_"))
async def cb_share_link(callback: CallbackQuery, bot: Bot):
    contest_id = int(callback.data.replace("share_link_", ""))
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=c_{contest_id}"
    await callback.message.answer(
        f"🔗 <b>Konkurs havolasi:</b>\n<code>{link}</code>\n\n<i>Ushbu havolani kanalingiz yoki do'stlaringizga yuboring!</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("view_parts_"))
async def cb_view_participants(callback: CallbackQuery):
    contest_id = int(callback.data.replace("view_parts_", ""))
    participants = await db.get_participants(contest_id)

    if not participants:
        await callback.answer("👥 Ushbu konkursda hali ishtirokchilar yo'q.", show_alert=True)
        return

    text = f"👥 <b>ISHTIROKCHILAR RO'YXATI (#{contest_id}):</b>\nJami: {len(participants)} ta\n━━━━━━━━━━━━━━━━━━━━━\n"
    for p in participants[:30]:  # Maksimal dastlabki 30 tasini ko'rsatish
        u_name = f"(@{p['username']})" if p['username'] else ""
        text += f"🎫 #{p['ticket_num']} <b>{p['full_name']}</b> {u_name}\n"

    if len(participants) > 30:
        text += f"\n<i>... va yana {len(participants) - 30} ta ishtirokchi</i>"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀️ Ortga", callback_data=f"manage_contest_{contest_id}")]]
    )
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("view_winners_"))
async def cb_view_winners(callback: CallbackQuery):
    contest_id = int(callback.data.replace("view_winners_", ""))
    contest = await db.get_contest(contest_id)
    winners = await db.get_winners(contest_id)

    if not winners:
        await callback.answer("G'oliblar hali aniqlanmagan.", show_alert=True)
        return

    podium = format_winners_podium(contest['title'], winners)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀️ Ortga", callback_data=f"manage_contest_{contest_id}")]]
    )
    await callback.message.edit_text(podium, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("end_confirm_"))
async def cb_end_confirm(callback: CallbackQuery):
    contest_id = int(callback.data.replace("end_confirm_", ""))
    text = (
        "⚠️ <b>DIQQAT! Konkursni yakunlamoqchimisiz?</b>\n\n"
        "Konkurs yakunlangach yangi ishtirokchilar qabul qilinmaydi."
    )
    await callback.message.edit_text(text, reply_markup=end_confirm_keyboard(contest_id), parse_mode="HTML")

@router.callback_query(F.data.startswith("do_end_"))
async def cb_do_end(callback: CallbackQuery):
    contest_id = int(callback.data.replace("do_end_", ""))
    await db.finish_contest(contest_id)
    await callback.answer("✅ Konkurs muvaffaqiyatli yakunlandi!", show_alert=True)
    await cb_manage_contest(callback, callback.bot)

# ========================================================
# 🎰 30 SEKUNDLIK 3 BOSQICHLI HAYAJONLI NEON BARABAN
# ========================================================

async def run_suspense_drum(
    bot: Bot,
    chat_id: int,
    message_id: int,
    place_num: int,
    place_name: str,
    pool: List[Dict[str, Any]],
    duration_seconds: int = 30,
    interval: float = 2.0
) -> Dict[str, Any]:
    """
    30 soniya davomida hayajonli baraban animatsiyasini aylantiradi
    va g'olibni aniqlaydi.
    """
    seconds_left = duration_seconds
    sample_pool = pool.copy()

    while seconds_left > 0:
        random.shuffle(sample_pool)
        candidate_names = [
            f"{p['full_name']} (@{p['username']})" if p['username'] else p['full_name']
            for p in sample_pool[:4]
        ]
        if len(candidate_names) < 3:
            candidate_names += ["🔮 Sirli Ishtirokchi", "⚡️ Cyber Nomzod"]

        frame_text = generate_drum_frame(
            round_num=place_num,
            place_name=place_name,
            seconds_left=seconds_left,
            current_names=candidate_names
        )

        try:
            await bot.edit_message_text(
                text=frame_text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="HTML"
            )
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramBadRequest:
            pass
        except Exception as err:
            logger.warning(f"Animatsiya yangilanishida xatolik: {err}")

        await asyncio.sleep(interval)
        seconds_left -= int(interval)

    # 30 soniya tugagach: G'olib tasodifiy tanlanadi
    winner = random.choice(pool)
    return winner

@router.callback_query(F.data.startswith("spin_contest_"))
async def cb_spin_contest(callback: CallbackQuery, bot: Bot):
    contest_id = int(callback.data.replace("spin_contest_", ""))
    contest = await db.get_contest(contest_id)

    if not contest:
        await callback.answer("❌ Konkurs topilmadi!", show_alert=True)
        return

    # Faqat konkurs egasi aylantira oladi
    if contest['creator_id'] != callback.from_user.id:
        await callback.answer("❌ Siz ushbu konkurs egasi emassiz!", show_alert=True)
        return

    participants = await db.get_participants(contest_id)
    if len(participants) < 3:
        await callback.answer(
            f"⚠️ 1, 2, va 3-o'rinlarni aniqlash uchun kamida 3 ta ishtirokchi kerak!\nHozirda: {len(participants)} ta",
            show_alert=True
        )
        return

    # BARABAN OLDIDAN BARCHA QATNASHUVCHILARNING OBUNASINI TEKSHIRISH
    await callback.message.edit_text(
        "🔍 <i>Ishtirokchilarning kanallarga obunasi tekshirilmoqda (chiqib ketganlar saralanmoqda)...</i>",
        parse_mode="HTML"
    )

    valid_participants = []
    removed_count = 0
    bot_info = await bot.get_me()

    for p in participants:
        is_main_sub, _ = await check_subscription(bot, MAIN_CHANNEL, p['user_id'])
        is_req_sub = True
        if contest['required_channel']:
            is_req_sub, _ = await check_subscription(bot, contest['required_channel'], p['user_id'])

        if is_main_sub and is_req_sub:
            valid_participants.append(p)
        else:
            # Obunani bekor qilgan foydalanuvchini konkursdan chiqarish
            await db.remove_participant(contest_id, p['user_id'])
            removed_count += 1
            try:
                contest_link = f"https://t.me/{bot_info.username}?start=c_{contest_id}"
                leave_warn = f"""
⚠️ <b>DIQQAT! KONKURSDAN CHIQARILDINGIZ!</b> ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━
Siz <b>{contest['title']}</b> (#ID: {contest_id}) konkursi majburiy kanalidan chiqib ketgansiz!
Shu sababli siz konkurs ishtirokchilari safidan chiqarildingiz.

🔄 <i>Qayta qatnashish uchun kanallarga qayta a'zo bo'ling va ushbu havola orqali tasdiqlang:</i>
<code>{contest_link}</code>
"""
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="🔄 Qayta a'zo bo'lish", url=contest_link)
                    ]]
                )
                await bot.send_message(p['user_id'], leave_warn.strip(), reply_markup=kb, parse_mode="HTML")
            except Exception:
                pass

    if len(valid_participants) < 3:
        warn_msg = (
            f"⚠️ <b>BARABANNI AYLANTIRIB BO'LMAYDI!</b>\n\n"
            f"Obunani bekor qilgan <b>{removed_count} ta</b> foydalanuvchi konkursdan chiqarildi.\n"
            f"Hozirda haqiqiy a'zo bo'lganlar soni: <b>{len(valid_participants)} ta</b>.\n"
            f"1, 2 va 3-o'rinlarni aniqlash uchun kamida <b>3 ta</b> faol ishtirokchi kerak!"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="📋 Boshqaruv paneli", callback_data=f"manage_contest_{contest_id}")]]
        )
        await callback.message.edit_text(warn_msg, reply_markup=kb, parse_mode="HTML")
        return

    await callback.answer("🎰 Neon Baraban ishga tushirildi! Har bir o'rin uchun 30 soniya aylanadi!", show_alert=False)

    # Avvalgi g'oliblarni tozalash (agar qayta aylantirilayotgan bo'lsa)
    await db.clear_winners(contest_id)

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    remaining_pool = valid_participants.copy()
    places_info = [
        (1, "🥇 1-O'RIN (BOSH SOVRIN)"),
        (2, "🥈 2-O'RIN"),
        (3, "🥉 3-O'RIN")
    ]

    selected_winners = []

    for place_num, place_label in places_info:
        # Har bir bosqich boshida ogohlantirish
        round_intro = f"""
⚡️━━━━━━━━━━━━━━━━━━━━━━━━━━⚡️
   🎲 <b>{place_label} UCHUN BARABAN BOSHLANMOQDA!</b>
⚡️━━━━━━━━━━━━━━━━━━━━━━━━━━⚡️
⏳ <i>Baraban 30 soniya aylanadi... Tayyormisiz?!</i>
"""
        await bot.edit_message_text(round_intro, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
        await asyncio.sleep(2)

        # 30 sekundlik hayajonli animatsiyani yurgizish
        winner = await run_suspense_drum(
            bot=bot,
            chat_id=chat_id,
            message_id=message_id,
            place_num=place_num,
            place_name=place_label,
            pool=remaining_pool,
            duration_seconds=30,
            interval=2.0
        )

        # G'olibni bazaga saqlash va ro'yxatdan chiqarish
        await db.save_winner(
            contest_id=contest_id,
            place=place_num,
            user_id=winner['user_id'],
            full_name=winner['full_name'],
            username=winner['username']
        )
        selected_winners.append({
            'place': place_num,
            'user_id': winner['user_id'],
            'full_name': winner['full_name'],
            'username': winner['username']
        })
        remaining_pool.remove(winner)

        # G'olibni e'lon qilish
        u_name = f"(@{winner['username']})" if winner['username'] else ""
        reveal_msg = f"""
🎯━━━━━━━━━━━━━━━━━━━━━━━━━━🎯
   🎉 <b>{place_label} ANIQLANDI!</b> 🎉
🎯━━━━━━━━━━━━━━━━━━━━━━━━━━🎯

👑 <b>G'olib:</b> <b>{winner['full_name']}</b> {u_name}
🎫 <b>Chipta raqami:</b> #{winner['ticket_num']}
🆔 <b>ID:</b> <code>{winner['user_id']}</code>

<i>Keyingi o'rin uchun tayyorgarlik ko'rilmoqda...</i>
"""
        await bot.edit_message_text(reveal_msg, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
        await asyncio.sleep(3)

    # 3 ta bosqich to'liq yakunlangach: Final Shohsupasi
    final_podium = format_winners_podium(contest['title'], selected_winners)
    final_podium += "\n\n🏁 <b>Konkurs g'oliblari aniqlandi! Konkursni yakunlashni xohlaysizmi?</b>"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛑 Konkursni yakunlash",
                    callback_data=f"end_confirm_{contest_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Boshqaruv paneli",
                    callback_data=f"manage_contest_{contest_id}"
                )
            ]
        ]
    )

    await bot.edit_message_text(final_podium, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML")
