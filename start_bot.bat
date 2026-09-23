@echo off
title Neon Giveaway Bot 24/7
cd /d "%~dp0"

echo =======================================================
echo ⚡️ NEON TELEGRAM BOT 24/7 AUTO-RESTART ISHGA TUSHDI
echo =======================================================

:loop
echo [%date% %time%] Bot ishga tushirilmoqda...
python main.py
echo [%date% %time%] Bot to'xtadi yoki xatolik yuz berdi. 5 soniyadan so'ng qayta ishga tushadi...
timeout /t 5 /nobreak >nul
goto loop
