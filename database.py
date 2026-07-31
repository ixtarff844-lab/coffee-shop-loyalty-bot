"""
Простой слой работы с БД на SQLite (через aiosqlite).
Таблицы:
  users        — telegram_id, phone, points, registered_at
  transactions — история начислений/списаний баллов (для истории у продавца)
"""

import aiosqlite
from datetime import datetime

DB_PATH = "coffee_bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                phone       TEXT UNIQUE,
                full_name   TEXT,
                points      REAL DEFAULT 0,
                registered_at TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone       TEXT,
                amount      REAL,        -- сумма заказа в рублях (может быть NULL)
                points_delta REAL,       -- сколько баллов начислено (+) или списано (-)
                admin_id    INTEGER,
                created_at  TEXT
            )
            """
        )
        await db.commit()


async def get_user_by_telegram_id(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        return await cursor.fetchone()


async def get_user_by_phone(phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE phone = ?", (phone,)
        )
        return await cursor.fetchone()


async def register_user(telegram_id: int, phone: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, phone, full_name, points, registered_at)
            VALUES (?, ?, ?, 0, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET phone = excluded.phone
            """,
            (telegram_id, phone, full_name, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def update_points_by_phone(phone: str, points_delta: float, amount: float | None, admin_id: int):
    """Начисляет (points_delta > 0) или списывает (points_delta < 0) баллы.
    Возвращает новый баланс баллов или None, если пользователь не найден."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        user = await cursor.fetchone()
        if user is None:
            return None

        new_points = max(0, user["points"] + points_delta)  # баллы не уходят в минус
        await db.execute(
            "UPDATE users SET points = ? WHERE phone = ?", (new_points, phone)
        )
        await db.execute(
            """
            INSERT INTO transactions (phone, amount, points_delta, admin_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (phone, amount, points_delta, admin_id, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return new_points
