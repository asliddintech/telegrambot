import asyncio
import logging
import random
import re
from typing import List

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

from states.states import CustomWheel
from keyboards.reply import main_menu_keyboard, cancel_keyboard
from keyboards.inline import custom_wheel_keyboard
from utils.neon_ui import generate_drum_frame

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🎰 Random Baraban")
async def start_custom_wheel(message: Message, state: FSMContext):
    await state.set_state(CustomWheel.waiting_for_items)
    text = """
🎰 <b>MUSTAQIL NEON RANDOM BARABAN</b> 🎰
━━━━━━━━━━━━━━━━━━━━━━━━━━
Bu yerda istalgan nomlar, ishtirokchilar yoki sovg'alarni kiritib, <b>30 sekundlik hayajonli baraban</b> yordamida tasodifiy g'olibni aniqlashingiz mumkin!

✍️ <b>Nomlarni yuboring:</b>
Variantlarni har birini <b>yangi qatorda</b> yoki <b>vergul (,)</b> bilan ajratib yozing.

<i>Masalan:
Akmal
Dilshod
Shohruh
Zilola
Bobur</i>
"""
    await message.answer(text.strip(), reply_markup=cancel_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "restart_custom_wheel")
async def cb_restart_wheel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CustomWheel.waiting_for_items)
    text = "✍️ <b>Yangi nomlarni yuboring (har birini yangi qatorda yoki vergul bilan):</b>"
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.message(CustomWheel.waiting_for_items)
async def process_wheel_items(message: Message, state: FSMContext):
    raw_text = message.text.strip()

    # Yangi qator yoki vergul orqali ajratish
    if "\n" in raw_text:
        items = [i.strip() for i in raw_text.split("\n") if i.strip()]
    elif "," in raw_text:
        items = [i.strip() for i in raw_text.split(",") if i.strip()]
    else:
        items = [i.strip() for i in raw_text.split() if i.strip()]

    # Kamida 2 ta nom bo'lishi kerak
    if len(items) < 2:
        await message.answer(
            "⚠️ Kamida <b>2 ta</b> nom yoki variant kiritishingiz kerak! Qaytadan yozing:",
            parse_mode="HTML"
        )
        return

    if len(items) > 500:
        await message.answer("⚠️ Maksimal 500 tagacha nom kiritish mumkin. Qaytadan kiriting:")
        return

    await state.update_data(wheel_items=items)

    preview_list = ""
    for idx, item in enumerate(items[:15], start=1):
        preview_list += f"{idx}. <b>{item}</b>\n"
    if len(items) > 15:
        preview_list += f"<i>... va yana {len(items) - 15} ta nom</i>\n"

    confirm_text = f"""
🎰 <b>BARABAN TAYYOR!</b> 🎰
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Kiritilgan nomlar soni:</b> {len(items)} ta

{preview_list}
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Barabanni aylantirish uchun pastdagi tugmani bosing (aylanish vaqti: 30 sekund)!</i>
"""
    await message.answer(
        confirm_text.strip(),
        reply_markup=custom_wheel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "spin_custom_wheel")
async def cb_spin_custom_wheel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    items = data.get("wheel_items", [])

    if not items or len(items) < 2:
        await callback.answer("⚠️ Avval nomlar ro'yxatini kiriting!", show_alert=True)
        return

    await callback.answer("🎰 30 sekundlik hayajonli baraban boshlandi!", show_alert=False)

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    duration = 30
    interval = 2.0
    seconds_left = duration
    sample_pool = items.copy()

    while seconds_left > 0:
        random.shuffle(sample_pool)
        candidate_names = sample_pool[:4]
        if len(candidate_names) < 3:
            candidate_names += ["🔮 Variant X", "⚡️ Omadli"]

        frame_text = generate_drum_frame(
            round_num=1,
            place_name="RANDOM G'OLIB",
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
            logger.warning(f"Custom baraban yangilashida xatolik: {err}")

        await asyncio.sleep(interval)
        seconds_left -= int(interval)

    # 30 soniya tugagach: g'olib aniqlanadi
    winner = random.choice(items)

    result_text = f"""
🏆━━━━━━━━━━━━━━━━━━━━━━━━━━🏆
   🎉 <b>RANDOM BARABAN G'OLIBI!</b> 🎉
🏆━━━━━━━━━━━━━━━━━━━━━━━━━━🏆

👑 <b>G'olib:</b>
⚡️┏━━━━━━━━━━━━━━━━━━━━┓⚡️
      💎 <b>{winner.upper()}</b> 💎
⚡️┗━━━━━━━━━━━━━━━━━━━━┛⚡️

📊 <i>Jami {len(items)} ta nom ichidan tasodifiy tanlandi!</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Yana aylantirishni xohlaysizmi?</i>
"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎡 Yana aylantirish (30s)",
                    callback_data="spin_custom_wheel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Boshqa nomlar kiritish",
                    callback_data="restart_custom_wheel"
                )
            ]
        ]
    )

    await bot.edit_message_text(
        result_text.strip(),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=kb,
        parse_mode="HTML"
    )
