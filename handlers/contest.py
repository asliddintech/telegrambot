import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import db
from config import MAIN_CHANNEL, MAIN_CHANNEL_URL
from states.states import ContestCreation
from keyboards.reply import main_menu_keyboard, cancel_keyboard, skip_or_cancel_keyboard
from keyboards.inline import creator_sub_check_keyboard
from utils.checker import check_subscription, clean_channel_username
from utils.neon_ui import neon_banner

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "⚡️ Yangi Konkurs yaratish")
async def start_contest_creation(message: Message, state: FSMContext):
    await state.clear()
    text = f"""
⚡️ <b>KONKURS YARATISH SHARTI</b> ⚡️
━━━━━━━━━━━━━━━━━━━━━━━━━━
Yangi konkurs yaratish uchun homiy kanalimizga obuna bo'lishingiz shart:
👉 <a href="{MAIN_CHANNEL_URL}">Developer Asliddin ({MAIN_CHANNEL})</a>

Kanalga a'zo bo'lgach, quyidagi <b>"✅ Obunani tekshirish"</b> tugmasini bosing!
"""
    await message.answer(
        text.strip(),
        reply_markup=creator_sub_check_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.callback_query(F.data == "verify_creator_sub")
async def cb_verify_creator_sub(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    is_sub, _ = await check_subscription(bot, MAIN_CHANNEL, user_id)

    if not is_sub:
        await callback.answer(
            "⚠️ Siz hali @developer_asliddin kanaliga a'zo emassiz!\nIltimos, avval kanalga obuna bo'ling.",
            show_alert=True
        )
        return

    await callback.answer("✅ Obuna tasdiqlandi!", show_alert=False)
    await state.set_state(ContestCreation.title)

    text = f"""
✅ <b>OBUNA TASDIQLANDI!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡️ <b>1-QADAM: KONKURS NOMINI KIRITING</b> ⚡️
━━━━━━━━━━━━━━━━━━━━━━━━━━
Konkursingiz uchun jozibali nom yozing.
<i>Masalan: 🔮 Neon Cyber Giveaway 2026</i>
"""
    await callback.message.answer(text.strip(), reply_markup=cancel_keyboard(), parse_mode="HTML")

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ <b>Jarayon bekor qilindi.</b>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(ContestCreation.title)
async def process_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 3 or len(title) > 100:
        await message.answer("⚠️ Konkurs nomi 3 tadan 100 tagacha belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return

    await state.update_data(title=title)
    await state.set_state(ContestCreation.description)
    text = f"""
📝 <b>2-QADAM: KONKURS TAVSIFI VA SOVG'ALARINI KIRITING</b> 📝
━━━━━━━━━━━━━━━━━━━━━━━━━━
Ishtirokchilar nimani yutib olishi mumkinligi va shartlarini yozing.
<i>Masalan:
🥇 1-o'rin: Telegram Premium (1 yil)
🥈 2-o'rin: 50$ pul mukofoti
🥉 3-o'rin: Dasturlash bo'yicha maxsus kurs</i>
"""
    await message.answer(text.strip(), reply_markup=cancel_keyboard(), parse_mode="HTML")

@router.message(ContestCreation.description)
async def process_description(message: Message, state: FSMContext):
    desc = message.text.strip()
    if len(desc) < 5 or len(desc) > 1000:
        await message.answer("⚠️ Tavsif 5 tadan 1000 tagacha belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return

    await state.update_data(description=desc)
    await state.set_state(ContestCreation.channel)
    text = f"""
📢 <b>3-QADAM: O'Z KANALINGIZNI QO'SHING</b> 📢
━━━━━━━━━━━━━━━━━━━━━━━━━━
Ishtirokchilar obuna bo'lishi kerak bo'lgan o'z kanalingizning havolasi yoki @username ini yuboring.
<i>Masalan: @mening_kanalim yoki https://t.me/mening_kanalim</i>

💡 <b>MUHIM:</b> Bot a'zolikni avtomatik tekshirishi uchun botni kanalingizga <b>admin</b> qilib qo'shishingiz kerak!

<i>Agar qo'shimcha kanal shart bo'lmasa, pastdagi "⏭ O'tkazib yuborish" tugmasini bosing:</i>
"""
    await message.answer(text.strip(), reply_markup=skip_or_cancel_keyboard(), parse_mode="HTML")

@router.message(ContestCreation.channel, F.text == "⏭ O'tkazib yuborish")
async def process_channel_skip(message: Message, state: FSMContext):
    await state.update_data(channel=None)
    await ask_target_count(message, state)

@router.message(ContestCreation.channel)
async def process_channel(message: Message, state: FSMContext):
    channel_input = message.text.strip()
    cleaned = clean_channel_username(channel_input)

    if not cleaned or len(cleaned) < 4:
        await message.answer("⚠️ Kanal manzili noto'g'ri ko'rinadi. Iltimos @kanal_nomi ko'rinishida yuboring yoki 'O'tkazib yuborish' tugmasini bosing:")
        return

    await state.update_data(channel=cleaned)
    await ask_target_count(message, state)

async def ask_target_count(message: Message, state: FSMContext):
    await state.set_state(ContestCreation.target_count)
    text = f"""
👥 <b>4-QADAM: KERAKLI ISHTIROKCHILAR SONI</b> 👥
━━━━━━━━━━━━━━━━━━━━━━━━━━
Konkursda g'olibni aniqlash (barabanni aylantirish) uchun kamida qancha ishtirokchi yig'ilishi kerak?
<i>Masalan: 20 (kamida 3 ta bo'lishi lozim)</i>
"""
    await message.answer(text.strip(), reply_markup=cancel_keyboard(), parse_mode="HTML")

@router.message(ContestCreation.target_count)
async def process_target_count(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, faqat musbat butun son kiriting (masalan: 25):")
        return

    target = int(text)
    if target < 3:
        await message.answer("⚠️ 1, 2 va 3-o'rinlarni aniqlash uchun kamida 3 ta ishtirokchi kiritilishi kerak:")
        return
    if target > 100000:
        await message.answer("⚠️ Ishtirokchilar soni juda katta (maksimal 100,000):")
        return

    data = await state.get_data()
    await state.clear()

    creator_id = message.from_user.id
    contest_id = await db.create_contest(
        creator_id=creator_id,
        title=data['title'],
        description=data['description'],
        required_channel=data.get('channel'),
        target_count=target
    )

    bot_info = await bot.get_me()
    contest_link = f"https://t.me/{bot_info.username}?start=c_{contest_id}"

    channel_info = data.get('channel') or "Qo'shimcha kanal yo'q (Faqat Asosiy kanal)"

    success_text = f"""
⚡️┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓⚡️
   🎉 <b>KONKURS MUVAFFAQIYATLI YARATILDI!</b> 🎉
⚡️┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛⚡️

🏆 <b>Nomi:</b> <code>{data['title']}</code>
📝 <b>Tavsif:</b> <i>{data['description']}</i>
📢 <b>Talab qilinadigan kanal:</b> <code>{channel_info}</code>
👥 <b>Maqsad:</b> <b>{target} ta</b> ishtirokchi

🔗 <b>Sizning Konkurs Havolangiz:</b>
<code>{contest_link}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <i>Ushbu havolani kanalingizga, do'stlaringizga yoki guruhlarga tarqating. Ular havola orqali kirib kanallaringizga obuna bo'lishadi!</i>
"""
    await message.answer(
        success_text.strip(),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
