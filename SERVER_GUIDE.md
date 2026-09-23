# 🌐 Botni Serverga Joylash va 24/7 Doimiy Ishlatish Qo'llanmasi

Ushbu loyiha botni xohlagan serverda (Linux VPS, Docker yoki Windows) 24/7 uzluksiz, avtomatik qayta ishga tushuvchi rejimda ishlatish uchun to'liq moslashtirildi.

---

## 1-USUL: 100% Bepul Bulutli Serverga Joylash (Render.com / Koyeb)

> 💡 **Firebase haqida muhim eslatma:** Firebase'ning bepul tarifi (*Spark Plan*) Telegram API'ga (`api.telegram.org`) chiquvchi so'rovlarni bloklaydi (tashqi internetga ulanish faqat pullik *Blaze* tarifida ishlaydi) hamda Firebase faqat statik saytlar yoki qisqa muddatli serverless funksiyalar uchun mo'ljallangan bo'lib, Telegram botlarining doimiy uzluksiz (`polling`) ishlashini qo'llab-quvvatlamaydi.
> Shu sababli Telegram botlar uchun quyidagi **100% bepul va doimiy ishlovchi bulutli platformalar** eng mukammal variant hisoblanadi:

### Render.com (100% Bepul va Oson):
Loyiha ichiga maxsus `render.yaml` va `Procfile` fayllari kiritildi.
1. [Render.com](https://render.com) saytiga kiring va ro'yxatdan o'ting.
2. **New +** tugmasini bosing va **Web Service** ni tanlang.
3. Loyihani GitHub orqali ulang (yoki fayllarni yuklang).
4. Quyidagi parametrlarni kiriting:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. **Environment Variables** bo'limida o'zgaruvchilarni kiriting:
   - `BOT_TOKEN` = `8837178501:AAG_J0V2fE3ya4B7CtkGOfSFxbb2AcQ367g`
   - `MAIN_CHANNEL` = `@developer_asliddin`
   - `MAIN_CHANNEL_URL` = `https://t.me/developer_asliddin`
6. **Create Web Service** tugmasini bosing.
7. Botni umuman uxlamasligi uchun [UptimeRobot.com](https://uptimerobot.com) bepul xizmatiga Render bergan havolani (masalan: `https://neon-giveaway-bot.onrender.com`) qo'shib qo'ying — bot **24/7 mutlaqo bepul** to'xtovsiz ishlaydi!

---

## 2-USUL: Linux VPS Serverga Joylash (Ubuntu / Debian) — Tavsiya etiladi

Agar sizda Linux VPS (masalan: Hetzner, Timeweb, DigitalOcean, VDSina) bo'lsa:

### 1-qadam: Serverga fayllarni yuklash
Serveringizga SSH orqali kiring va loyihani yuklang (masalan `/root/bot` papkasiga).

### 2-qadam: 1-Click Avtomatik O'rnatish
Papka ichida quyidagi buyruqni bering:
```bash
chmod +x deploy.sh
./deploy.sh
```
Ushbu skript avtomatik ravishda:
- Kerakli Python paketlarini o'rnatadi;
- Virtual muhit (venv) yaratadi;
- Kutubxonalarni o'rnatadi;
- `neon_bot.service` ni `/etc/systemd/system/` ga joylaydi;
- Botni fon rejimida 24/7 ishga tushiradi va server o'chib-yonsa ham avtomatik qayta ishga tushadigan qilib sozlaydi.

### Holatni tekshirish va boshqarish:
- Bot holati: `systemctl status neon_bot`
- Jonli loglarni ko'rish: `journalctl -u neon_bot -f`
- Qayta ishga tushirish: `systemctl restart neon_bot`
- To'xtatish: `systemctl stop neon_bot`

---

## 2-USUL: Docker & Docker Compose Orqali Ishga Tushirish

Agar serveringizda Docker o'rnatilgan bo'lsa, atigi 1 ta buyruq bilan ishga tushirishingiz mumkin:

```bash
docker compose up -d --build
```

- Konteyner holati: `docker ps`
- Loglarni ko'rish: `docker logs -f neon_giveaway_bot`
- To'xtatish: `docker compose down`

`restart: always` parametri sababli bot xatolik yuz bersa yoki server qayta yuklansa ham darhol avtomatik o'zi ishga tushadi.

---

## 3-USUL: Hozirgi Kompyuterda 24/7 Avtomatik Ishlatish (Allaqachon sozlandi!)

Hozirgi kompyuteringizda:
1. `start_bot.bat` — bot to'xtab qolsa avtomatik 5 soniyadan so'ng qayta yoquvchi cheksiz tsikl skripti yaratildi.
2. `run_silent.vbs` — konsol oynasi ko'rinmasdan, yashirin fonda ishlatadi.
3. **Windows Autostart sozlandi:** Windows Startup papkasiga yorliq joylashtirildi. Kompyuter yoqilganda bot avtomatik fonda ishga tushadi.

---

## 🔐 Xavfsizlik va Ma'lumotlar Bazasi
- `bot.db` — barcha konkurslar, ishtirokchilar va g'oliblar bazasi.
- `.env` — token va kanal sozlamalari.
Serverga ko'chirganda ushbu ikkala faylni birga ko'chirish kifoya.
