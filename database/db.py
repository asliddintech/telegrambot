import aiosqlite
from typing import Optional, List, Dict, Any
from config import DB_PATH

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Ma'lumotlar bazasi jadvallarini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS contests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    required_channel TEXT,
                    target_count INTEGER DEFAULT 10,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contest_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    full_name TEXT,
                    username TEXT,
                    ticket_num INTEGER NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(contest_id, user_id),
                    FOREIGN KEY(contest_id) REFERENCES contests(id) ON DELETE CASCADE
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS winners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contest_id INTEGER NOT NULL,
                    place INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    full_name TEXT,
                    username TEXT,
                    won_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(contest_id) REFERENCES contests(id) ON DELETE CASCADE
                )
            """)
            await db.commit()

    async def add_user(self, user_id: int, full_name: str, username: Optional[str]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, full_name, username)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    username = excluded.username
            """, (user_id, full_name, username))
            await db.commit()

    async def create_contest(self, creator_id: int, title: str, description: str,
                             required_channel: Optional[str], target_count: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO contests (creator_id, title, description, required_channel, target_count)
                VALUES (?, ?, ?, ?, ?)
            """, (creator_id, title, description, required_channel, target_count))
            await db.commit()
            return cursor.lastrowid

    async def get_contest(self, contest_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM contests WHERE id = ?", (contest_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_user_contests(self, creator_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM contests WHERE creator_id = ? ORDER BY id DESC",
                (creator_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def is_participant(self, contest_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id FROM participants WHERE contest_id = ? AND user_id = ?",
                (contest_id, user_id)
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def add_participant(self, contest_id: int, user_id: int, full_name: str, username: Optional[str]) -> Optional[int]:
        """Ishtirokchini qo'shadi va uning chipta raqamini (ticket_num) qaytaradi. Agar allaqachon bo'lsa None."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Joriy qatnashuvchilar sonini aniqlash
                async with db.execute(
                    "SELECT COUNT(*) FROM participants WHERE contest_id = ?", (contest_id,)
                ) as cursor:
                    count_row = await cursor.fetchone()
                    ticket_num = (count_row[0] if count_row else 0) + 1

                await db.execute("""
                    INSERT INTO participants (contest_id, user_id, full_name, username, ticket_num)
                    VALUES (?, ?, ?, ?, ?)
                """, (contest_id, user_id, full_name, username, ticket_num))
                await db.commit()
                return ticket_num
            except aiosqlite.IntegrityError:
                return None

    async def remove_participant(self, contest_id: int, user_id: int) -> bool:
        """Ishtirokchini konkursdan o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM participants WHERE contest_id = ? AND user_id = ?",
                (contest_id, user_id)
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_user_active_contests(self, user_id: int) -> List[Dict[str, Any]]:
        """Foydalanuvchi qatnashayotgan barcha faol konkurslar ro'yxati"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT c.* FROM contests c
                INNER JOIN participants p ON c.id = p.contest_id
                WHERE p.user_id = ? AND c.status = 'active'
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_participants_count(self, contest_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM participants WHERE contest_id = ?", (contest_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_participants(self, contest_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM participants WHERE contest_id = ? ORDER BY ticket_num ASC",
                (contest_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def save_winner(self, contest_id: int, place: int, user_id: int, full_name: str, username: Optional[str]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO winners (contest_id, place, user_id, full_name, username)
                VALUES (?, ?, ?, ?, ?)
            """, (contest_id, place, user_id, full_name, username))
            await db.commit()

    async def get_winners(self, contest_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM winners WHERE contest_id = ? ORDER BY place ASC",
                (contest_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def clear_winners(self, contest_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM winners WHERE contest_id = ?", (contest_id,))
            await db.commit()

    async def finish_contest(self, contest_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE contests SET status = 'finished' WHERE id = ?",
                (contest_id,)
            )
            await db.commit()

db = Database()
