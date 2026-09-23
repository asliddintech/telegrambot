# ⚡️ Neon Style Telegram Konkurs va Obuna Boti 🔮

Telegram kanallarga obunachilarni jalb qilish, konkurslar (giveaway) o'tkazish, 30 soniyali hayajonli Neon Baraban orqali g'oliblarni aniqlash va mustaqil Random Baraban menyusiga ega Telegram bot.

---

## 🚀 Asosiy Imkoniyatlar

1. **Majburiy Kanal A'zoligi:**
   - Asosiy kanal: `@developer_asliddin` (`https://t.me/developer_asliddin`).
   - Botdan foydalanish va har qanday konkursda ishtirok etish uchun ushbu kanalga a'zo bo'lish talab etiladi.
2. **Konkurs Yaratish:**
   - Konkurs nomi, tavsifi va sovg'alari.
   - Konkurs egasining o'z kanali (qo'shimcha majburiy shart).
   - Belgilangan ishtirokchilar soni (maqsad).
3. **Unikal Deep-Link Havolasi:**
   - Har bir konkurs uchun unikal havola generatsiya qilinadi: `https://t.me/randomrent_bot?start=c_<ID>`.
   - Ishtirokchilar havola orqali kirib barcha majburiy kanallarga obunani tasdiqlaydi va chipta raqamini oladi.
4. **🎰 30 Sekundlik 3 Bosqichli Neon Baraban:**
   - 🥇 **1-o'rin:** 30 soniyalik hayajonli aylanuvchi vizual baraban orqali aniqlanadi.
   - 🥈 **2-o'rin:** 30 soniyalik aylanuvchi baraban orqali aniqlanadi.
   - 🥉 **3-o'rin:** 30 soniyalik aylanuvchi baraban orqali aniqlanadi.
   - G'oliblar e'lon qilingach, konkursni yakunlash tasdig'i so'raladi.
5. **🎡 Mustaqil "Random Baraban" Menyusi:**
   - Istalgan odam o'zi xohlagan ismlar yoki sovg'alarni yozib barabanga joylashi mumkin.
   - 30 sekundlik hayajonli neon animatsiya bilan tasodifiy g'olib aniqlanadi.

---

## 🛠 O'rnatish va Ishga Tushirish

1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

2. `.env` faylida Bot Tokenini tekshirish:
```env
BOT_TOKEN=8837178501:AAG_J0V2fE3ya4B7CtkGOfSFxbb2AcQ367g
MAIN_CHANNEL=@developer_asliddin
MAIN_CHANNEL_URL=https://t.me/developer_asliddin
DB_PATH=bot.db
```

3. Botni ishga tushirish:
```bash
python main.py
```
