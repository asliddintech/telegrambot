import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import os
from aiohttp import web

from config import BOT_TOKEN
from database.db import db
from handlers import start, contest, manage, wheel

# Windows konsolida emojilar xatosiz chiqishi uchun UTF-8 ga sozlash
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NeonBot")

async def handle_health_check(request):
    """Bulutli serverlar uchun tiriklikni tasdiqlovchi endpoint"""
    return web.Response(
        text="⚡️ Neon Giveaway Telegram Bot is Running 24/7!\nStatus: OK",
        content_type="text/plain"
    )

async def start_health_server():
    """Render, Koyeb kabi bepul serverlar uchun web server"""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Health-check web server {port}-portda ishga tushirildi.")

async def main():
    logger.info("Bot ma'lumotlar bazasi ishga tushirilmoqda...")
    await db.init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Handler routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(contest.router)
    dp.include_router(manage.router)
    dp.include_router(wheel.router)

    # Bot ma'lumotlarini olish
    me = await bot.get_me()
    logger.info(f"⚡️ Neon Konkurs Boti muvaffaqiyatli ishga tushdi: @{me.username} (ID: {me.id})")
    print(f"\n=======================================================")
    print(f"🚀 NEON GIVEAWAY BOT ISHGA TUSHDI: @{me.username}")
    print(f"=======================================================\n")

    # Agar bulutli server muhiti bo'lsa (PORT berilgan bo'lsa), health-serverni yoqish
    if os.getenv("PORT") or os.getenv("ENABLE_WEB_SERVER"):
        await start_health_server()

    # Polling boshlash (eski kutilmagan yangilanishlarni o'tkazib yuborish)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi!")
