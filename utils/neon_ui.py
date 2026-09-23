"""
Neon UI - Cyberpunk & Neon uslubidagi estetik vizualizatsiya vositalari
"""
import random

def progress_bar(current: int, total: int, length: int = 10) -> str:
    """Neon uslubidagi progress bar yaratish"""
    if total <= 0:
        percent = 100
        filled = length
    else:
        percent = min(100, int((current / total) * 100))
        filled = int((current / total) * length)
        filled = min(length, max(0, filled))

    bar = "█" * filled + "░" * (length - filled)
    return f"┫{bar}┣ {percent}% ({current}/{total})"

def neon_banner(title: str, subtitle: str = "") -> str:
    """Neon uslubidagi sarlavha paneli"""
    line = "━" * 28
    res = f"⚡️┏{line}┓⚡️\n"
    res += f"   🔮 <b>{title.upper()}</b> 🔮\n"
    if subtitle:
        res += f"   🌌 <i>{subtitle}</i>\n"
    res += f"⚡️┗{line}┛⚡️"
    return res

def neon_box(content: str) -> str:
    return f"╭────────────── ❖ ──────────────╮\n{content}\n╰────────────── ❖ ──────────────╯"

def format_contest_card(contest: dict, current_participants: int, bot_username: str) -> str:
    """Konkurs kartasi matni"""
    link = f"https://t.me/{bot_username}?start=c_{contest['id']}"
    status_icon = "🟢 FAOLLIKDA" if contest['status'] == 'active' else "🔴 YAKUNLANGAN"
    p_bar = progress_bar(current_participants, contest['target_count'])

    card = f"""
⚡️ <b>NEON GIVEAWAY #{contest['id']}</b> ⚡️
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 <b>Nomi:</b> <code>{contest['title']}</code>
📝 <b>Tavsifi:</b>
<i>{contest['description']}</i>

📊 <b>Holati:</b> {status_icon}
👥 <b>Ishtirokchilar:</b>
{p_bar}

🔗 <b>Konkurs Havolasi:</b>
<code>{link}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>💎 Do'stlaringizni taklif qiling va obunani tasdiqlang!</i>
"""
    return card.strip()

def format_winners_podium(contest_title: str, winners: list) -> str:
    """G'oliblar shohsupasi"""
    podium = f"""
🏆━━━━━━━━━━━━━━━━━━━━━━━━━━🏆
   🎉 <b>G'OLIBLAR ANIQLANDI!</b> 🎉
🏆━━━━━━━━━━━━━━━━━━━━━━━━━━🏆

🎯 <b>Konkurs:</b> <code>{contest_title}</code>

"""
    places = {
        1: ("🥇 1-O'RIN (SUPER G'OLIB)", "👑"),
        2: ("🥈 2-O'RIN", "⭐"),
        3: ("🥉 3-O'RIN", "✨")
    }

    for w in winners:
        place_info, icon = places.get(w['place'], (f"🏅 {w['place']}-o'rin", "✨"))
        username_str = f"(@{w['username']})" if w['username'] else ""
        podium += f"{icon} <b>{place_info}:</b>\n"
        podium += f"   └ 👤 <b>{w['full_name']}</b> {username_str} [ID: <code>{w['user_id']}</code>]\n\n"

    podium += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    podium += "✨ <i>Barcha g'oliblarni chin yurakdan tabriklaymiz! 🎊</i>"
    return podium.strip()

# Neon Drum animatsiyasi ramzlari
DRUM_SYMBOLS = ["💎", "🔮", "⚡️", "👑", "🎯", "🚀", "🎰", "🔥", "💫", "✨"]

def generate_drum_frame(round_num: int, place_name: str, seconds_left: int, current_names: list) -> str:
    """30 soniyali hayajonli baraban aylanayotgandagi ramka"""
    sym1 = random.choice(DRUM_SYMBOLS)
    sym2 = random.choice(DRUM_SYMBOLS)
    sym3 = random.choice(DRUM_SYMBOLS)
    sym4 = random.choice(DRUM_SYMBOLS)

    # Ko'rinadigan aylanuvchi nomlar
    visible_names = ""
    for idx, name in enumerate(current_names[:3], start=1):
        if idx == 2:
            visible_names += f"   ▶️ <b>[ ⚡️ {name} ⚡️ ]</b> ◀️  (O'Q UCHIDA)\n"
        else:
            visible_names += f"      <i>{name}</i>\n"

    # Progress visual
    # 30 sekunddan qolgan vaqt
    total_time = 30
    elapsed = total_time - seconds_left
    dots_count = int((elapsed / total_time) * 15)
    neon_timeline = "▓" * dots_count + "░" * (15 - dots_count)

    text = f"""
🎰━━━━━━━━━━━━━━━━━━━━━━━━━━🎰
   ⚡️ <b>NEON RANDOM BARABAN</b> ⚡️
🎰━━━━━━━━━━━━━━━━━━━━━━━━━━🎰

🎯 <b>ANIQLANMOQDA:</b> <b>{place_name.upper()}</b>
⏳ <b>Qolgan vaqt:</b> <code>{seconds_left} sekund</code>
┫{neon_timeline}┣

🎲 <b>BARABAN AYLANMOQDA:</b>
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  {sym1}  │  {sym2}  │  {sym3}  │  {sym4}  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

🌀 <b>Hozir o'tayotgan ishtirokchilar:</b>
{visible_names}
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>🔥 Nafasni yutib kuting... Baraban sekinlashmoqda!</i>
"""
    return text.strip()
