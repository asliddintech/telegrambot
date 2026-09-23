import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT
from aiogram.fsm.context import FSMContext

from database.db import db
from config import MAIN_CHANNEL, MAIN_CHANNEL_URL
from keyboards.reply import main_menu_keyboard, cancel_keyboard
from keyboards.inline import contest_join_keyboard, welcome_inline_keyboard, creator_sub_check_keyboard
from states.states import CustomWheel
from utils.neon_ui import format_contest_card, neon_banner
from utils.checker import check_subscription, clean_channel_username

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user
    is_new_user = await db.add_user(user.id, user.full_name, user.username)

    bot_info = await bot.get_me()
    args = command.args

    # Agar foydalanuvchi deep-link orqali kirgan bo'lsa (masalan: /start c_5)
    if args and args.startswith("c_"):
        try:
            contest_id = int(args.replace("c_", ""))
            contest = await db.get_contest(contest_id)
            if not contest:
                await message.answer(
                    "❌ <b>Konkurs topilmadi yoki o'chirib yuborilgan!</b>",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="HTML"
                )
                return

            participants_count = await db.get_participants_count(contest_id)
            is_part = await db.is_participant(contest_id, user.id)

            if is_part:
                # Real vaqtda obunani qayta tekshiramiz: foydalanuvchi kanaldan chiqib ketmaganmi?
                is_main_sub, _ = await check_subscription(bot, MAIN_CHANNEL, user.id)
                is_req_sub = True
                if contest['required_channel']:
                    is_req_sub, _ = await check_subscription(bot, contest['required_channel'], user.id)

                if not (is_main_sub and is_req_sub):
                    # Obunani bekor qilgan! Ishtirokchilar safidan chiqaramiz
                    await db.remove_participant(contest_id, user.id)
                    participants_count = await db.get_participants_count(contest_id)
                    card_text = format_contest_card(contest, participants_count, bot_info.username)
                    card_text += (
                        "\n\n⚠️ <b>DIQQAT: Siz majburiy kanal(lar)dan chiqib ketgansiz!</b>\n"
                        "Shu sababli konkursdagi ishtirokingiz bekor qilindi.\n\n"
                        "👇 <i>Konkursga qayta qo'shilish uchun kanalga qayta a'zo bo'ling va quyidagi tugma orqali tasdiqlang:</i>"
                    )
                    await message.answer(
                        card_text,
                        reply_markup=contest_join_keyboard(contest_id, contest['required_channel']),
                        parse_mode="HTML"
                    )
                    return
                else:
                    card_text = format_contest_card(contest, participants_count, bot_info.username)
                    card_text += "\n\n✅ <b>Siz ushbu konkursda ishtirok etyapsiz! Omad! 🍀</b>"
                    await message.answer(
                        card_text,
                        reply_markup=main_menu_keyboard(),
                        parse_mode="HTML"
                    )
                    return
            else:
                card_text = format_contest_card(contest, participants_count, bot_info.username)
                card_text += "\n\n👇 <i>Konkursda qatnashish uchun quyidagi kanallarga a'zo bo'ling va tasdiqlang:</i>"
                await message.answer(
                    card_text,
                    reply_markup=contest_join_keyboard(contest_id, contest['required_channel']),
                    parse_mode="HTML"
                )
            return
        except ValueError:
            pass

    # Yangi va mavjud foydalanuvchilar uchun Neon uslubidagi to'liq ma'lumot
    greeting_title = "✨ XUSH KELIBSIZ!" if is_new_user else "👋 QAYTGANINGIZ BILAN!"

    welcome_text = f"""
⚡️┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓⚡️
   🔮 <b>NEON GIVEAWAY & CONTEST BOT</b> 🔮
   🌌 <i>Auditoriyangizni tez va oson yig'ing!</i>
⚡️┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛⚡️

{greeting_title} <b>{user.full_name}</b>! 💎

🤖 <b>BU BOT SIZGA QANDAY YORDAM BERADI?</b>
Bu bot Telegram kanallaringizga <b>jonli va faol obunachilar</b> to'plash, adolatli konkurslar (giveaway) o'tkazish hamda 30 soniyalik hayajonli baraban orqali g'oliblarni aniqlash uchun yaratilgan.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>ASOSIY IMKONIYaTLAR:</b>

1️⃣ <b>⚡️ Yangi Konkurs yaratish:</b>
   • O'z kanalingiz uchun unikal konkurs ochasiz;
   • Sovg'alar va kerakli ishtirokchilar sonini belgilaysiz;
   • Kanalingizni majburiy obuna sharti sifatida qo'shasiz.

2️⃣ <b>🛡 100% Majburiy Obuna Nazorati:</b>
   • Ishtirokchilar sizning kanalingizga va homiy kanalga (<a href="{MAIN_CHANNEL_URL}">@developer_asliddin</a>) a'zo bo'lmaguncha konkursda qatnasha olmaydi!
   • Kanaldan chiqib ketganlar avtomatik ro'yxatdan chetlatiladi.

3️⃣ <b>🎰 30 Sekundlik Hayajonli Baraban:</b>
   • Ishtirokchilar soni to'lgach, 3 bosqichda 30 soniyadan aylanuvchi vizual animatsiya orqali 🥇 1-o'rin, 🥈 2-o'rin va 🥉 3-o'rin aniqlanadi!

4️⃣ <b>🎡 Mustaqil Random Baraban:</b>
   • Konkursdan tashqari, istalgan nomlar, do'stlar yoki sovg'alarni yozib, 30 soniyada tasodifiy g'olibni aniqlashingiz mumkin.
━━━━━━━━━━━━━━━━━━━━━━━━━━

📢 <b>Asosiy homiy kanali:</b> <a href="{MAIN_CHANNEL_URL}">Developer Asliddin</a>

<i>Quyidagi menyu tugmalaridan birini tanlang va boshlang:</i>
"""
    await message.answer(
        welcome_text.strip(),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    # Qo'shimcha tezkor inline boshlash tugmalari
    await message.answer(
        "⚡️ <b>Tezkor amallar uchun quyidagi tugmalardan ham foydalanishingiz mumkin:</b>",
        reply_markup=welcome_inline_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("check_sub_"))
async def handle_check_subscription(callback: CallbackQuery, bot: Bot):
    contest_id = int(callback.data.replace("check_sub_", ""))
    user = callback.from_user
    contest = await db.get_contest(contest_id)

    if not contest:
        await callback.answer("❌ Konkurs topilmadi!", show_alert=True)
        return

    if contest['status'] != 'active':
        await callback.answer("🔴 Ushbu konkurs allaqachon yakunlangan!", show_alert=True)
        return

    # 1. Bosh majburiy kanalni tekshirish (@developer_asliddin)
    is_main_sub, err1 = await check_subscription(bot, MAIN_CHANNEL, user.id)
    if not is_main_sub:
        await callback.answer(
            f"⚠️ Siz @developer_asliddin kanaliga a'zo emassiz!\nIltimos, avval kanalga obuna bo'ling.",
            show_alert=True
        )
        return

    # 2. Qo'shimcha kanalni tekshirish (agar mavjud bo'lsa)
    if contest['required_channel']:
        is_req_sub, err2 = await check_subscription(bot, contest['required_channel'], user.id)
        if not is_req_sub:
            msg = err2 or f"⚠️ Siz {contest['required_channel']} kanaliga a'zo emassiz!\nIltimos, avval kanalga a'zo bo'ling."
            await callback.answer(msg, show_alert=True)
            return

    # 3. Ishtirokchini ro'yxatga olish
    ticket_num = await db.add_participant(contest_id, user.id, user.full_name, user.username)
    if ticket_num is None:
        await callback.answer("✅ Siz allaqachon ushbu konkurs ishtirokchisisiz!", show_alert=True)
        return

    # Muvaffaqiyatli qatnashdi!
    current_count = await db.get_participants_count(contest_id)
    bot_info = await bot.get_me()

    success_msg = f"""
🎉 <b>TABRIKLAYMIZ! OBUNA TASDIQLANDI!</b> 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━
🎫 Sizning ishtirokchi chiptangiz: <b>#{ticket_num}</b>
🎯 Konkurs: <b>{contest['title']}</b>
👥 Jami qatnashuvchilar: <b>{current_count}/{contest['target_count']}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>🍀 Sizga konkursda ulkan omad tilaymiz!</i>
"""
    await callback.message.edit_text(
        format_contest_card(contest, current_count, bot_info.username) + f"\n\n{success_msg}",
        parse_mode="HTML"
    )
    await callback.answer("🎉 Siz muvaffaqiyatli ro'yxatdan o'tdingiz!", show_alert=False)

    # Agar maqsadli songa yetgan bo'lsa, konkurs egasiga xabar berish
    if current_count >= contest['target_count']:
        try:
            target_reached_msg = f"""
⚡️ <b>DIQQAT! KONKURS MAQSADGA YETDI!</b> ⚡️
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 <b>Konkurs:</b> {contest['title']}
👥 Belgilangan <b>{contest['target_count']} ta</b> ishtirokchi to'liq yig'ildi!

🎰 Endi "Mening Konkurslarim" bo'limiga kirib, <b>Neon Barabanni aylantirishingiz</b> va 1, 2, 3-o'rin g'oliblarini aniqlashingiz mumkin!
"""
            await bot.send_message(contest['creator_id'], target_reached_msg, parse_mode="HTML")
        except Exception as e:
            logger.warning(f"Konkurs egasiga xabar yuborishda xatolik: {e}")

@router.callback_query(F.data == "start_create_contest_inline")
async def cb_start_create_contest_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = f"""
⚡️ <b>KONKURS YARATISH SHARTI</b> ⚡️
━━━━━━━━━━━━━━━━━━━━━━━━━━
Yangi konkurs yaratish uchun homiy kanalimizga obuna bo'lishingiz shart:
👉 <a href="{MAIN_CHANNEL_URL}">Developer Asliddin ({MAIN_CHANNEL})</a>

Kanalga a'zo bo'lgach, quyidagi <b>"✅ Obunani tekshirish"</b> tugmasini bosing!
"""
    await callback.message.answer(
        text.strip(),
        reply_markup=creator_sub_check_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "start_custom_wheel_inline")
async def cb_start_custom_wheel_inline(callback: CallbackQuery, state: FSMContext):
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
    await callback.message.answer(text.strip(), reply_markup=cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.message(F.text.startswith("ℹ️ Bot haqida"))
async def cmd_about(message: Message):
    about_text = f"""
🔮 <b>NEON GIVEAWAY BOT HAQIDA TO'LIQ QO'LLANMA</b> 🔮
━━━━━━━━━━━━━━━━━━━━━━━━━━
Ushbu bot Telegram kanallarini tez, xavfsiz va samarali rivojlantirish uchun yaratilgan zamonaviy tizimdir.

🚀 <b>ASOSIY IMKONIYaTLAR:</b>

1️⃣ <b>⚡️ Konkurs Yaratish:</b>
   • Konkurs nomi, mukofotlar tavsifi va qatnashuvchilar maqsadini kiriting.
   • O'z kanalingizni havola qilib qo'shing (botni kanalingizga admin qilish tavsiya etiladi).
   • Bot sizga tayyor unikal taklif havolasini taqdim etadi.

2️⃣ <b>🛡 A'zolikni Avtomatik Tekshirish:</b>
   • Har bir ishtirokchi kanallarga to'liq obuna bo'lmaguncha unga ishtirokchi chiptasi berilmaydi.
   • Agar ishtirokchi konkurs davomida kanaldan chiqib ketsa, bot uni avtomatik chetlatadi va ogohlantiradi.

3️⃣ <b>🎰 30 Sekundlik 3 Bosqichli Baraban:</b>
   • Maqsadli songa yetgach, konkurs egasi barabanni ishga tushiradi.
   • Har bir o'rin (🥇 1-o'rin, 🥈 2-o'rin, 🥉 3-o'rin) uchun alohida 30 soniyalik hayajonli neon vizual animatsiya aylanadi va g'oliblar tasodifiy aniqlanadi.

4️⃣ <b>🎡 Mustaqil Random Baraban:</b>
   • Do'stlaringiz davrasida yoki istalgan ro'yxat bo'yicha g'olibni aniqlash uchun nomlarni yozing va barabanni aylantiring.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 <b>Asosiy Homiy:</b> <a href="{MAIN_CHANNEL_URL}">Developer Asliddin</a>
👨‍💻 <b>Dasturchi:</b> @developer_asliddin
"""
    await message.answer(about_text, parse_mode="HTML", disable_web_page_preview=True)

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT))
async def on_user_left_channel(event: ChatMemberUpdated, bot: Bot):
    user = event.old_chat_member.user
    if user.is_bot:
        return

    chat = event.chat
    chat_username = f"@{chat.username.lower()}" if chat.username else ""
    chat_id_str = str(chat.id)

    # Foydalanuvchi qatnashayotgan barcha faol konkurslarni aniqlash
    active_contests = await db.get_user_active_contests(user.id)
    if not active_contests:
        return

    bot_info = await bot.get_me()

    for contest in active_contests:
        should_remove = False

        # 1. Bosh homiy kanali bo'lsa (@developer_asliddin)
        if chat_username == MAIN_CHANNEL.lower() or chat_id_str == MAIN_CHANNEL:
            should_remove = True
        # 2. Konkursning o'z kanali bo'lsa
        elif contest['required_channel']:
            req_clean = clean_channel_username(contest['required_channel']).lower()
            if req_clean == chat_username or req_clean == chat_id_str:
                should_remove = True

        if should_remove:
            removed = await db.remove_participant(contest['id'], user.id)
            if removed:
                contest_link = f"https://t.me/{bot_info.username}?start=c_{contest['id']}"
                channel_name = f"@{chat.username}" if chat.username else chat.title
                try:
                    alert_text = f"""
⚠️ <b>DIQQAT! SIZ KONKURSDAN CHIQARILDINGIZ!</b> ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━
Siz majburiy kanal (<b>{channel_name}</b>)dan chiqib ketganingiz sababli:
🎯 <b>{contest['title']}</b> (#ID: {contest['id']}) konkursidagi ishtirokingiz bekor qilindi.

🔄 <i>Konkursda qayta qatnashish uchun kanalga qayta obuna bo'ling va quyidagi havola orqali tasdiqlang:</i>
<code>{contest_link}</code>
"""
                    kb = InlineKeyboardMarkup(
                        inline_keyboard=[[
                            InlineKeyboardButton(text="🔄 Qayta qo'shilish", url=contest_link)
                        ]]
                    )
                    await bot.send_message(user.id, alert_text.strip(), reply_markup=kb, parse_mode="HTML")
                except Exception as err:
                    logger.warning(f"Foydalanuvchiga chiqib ketish xabari yuborilmadi: {err}")
