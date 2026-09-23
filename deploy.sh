#!/bin/bash
# Neon Telegram Bot - Linux VPS 1-Click O'rnatish Skripti

echo "⚡️ Neon Giveaway Botni serverga o'rnatish boshlandi..."

# Paketlarni yangilash
apt update && apt install -y python3 python3-pip python3-venv git

# Virtual muhit yaratish
python3 -m venv venv
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install --upgrade pip
pip install -r requirements.txt

# Systemd servisiga nusxalash
cp neon_bot.service /etc/systemd/system/neon_bot.service

# Servisni faollashtirish va ishga tushirish
systemctl daemon-reload
systemctl enable neon_bot
systemctl restart neon_bot

echo "✅ Bot muvaffaqiyatli serverga joylandi va 24/7 rejimda ishga tushirildi!"
echo "📊 Holatni tekshirish uchun: systemctl status neon_bot"
echo "📜 Loglarni ko'rish uchun: journalctl -u neon_bot -f"
