import aiosqlite
import sqlite3

from django import db
from config import DB_PATH
from datetime import datetime, timedelta

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, total_debt REAL DEFAULT 0.0, language TEXT DEFAULT 'kaa')''')
        await db.execute('''CREATE TABLE IF NOT EXISTS Invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, photo_id TEXT, comment TEXT, date TEXT, deadline_date TEXT, payment_type TEXT DEFAULT 'Товар', FOREIGN KEY(user_id) REFERENCES Users(id))''')
        await db.execute('''CREATE TABLE IF NOT EXISTS StoreSellers (id INTEGER PRIMARY KEY, full_name TEXT)''')
        await db.commit()

async def get_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM Users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def set_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE Users SET language = ? WHERE id = ?", (lang, user_id))
        await db.commit()

async def add_debt_to_db(user_id: int, amount: float, photo_id: str, comment: str, date_str: str, days: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO Invoices (user_id, amount, photo_id, comment, date, deadline_date, payment_type) VALUES (?, ?, ?, ?, ?, datetime(?, '+' || ? || ' days'), 'Товар')",
            (user_id, amount, photo_id, comment, date_str, date_str, days)
        )
        await db.execute("UPDATE Users SET total_debt = total_debt + ? WHERE id = ?", (amount, user_id))
        await db.commit()

async def get_active_debts(user_id: int):
    """Получить все активные долги пользователя (только тип 'Товар')"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM Invoices WHERE user_id = ? AND payment_type = 'Товар' ORDER BY date DESC", 
            (user_id,)
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]

async def reduce_debt_in_db(user_id: int, amount: float, payment_type: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO Invoices (user_id, amount, photo_id, comment, date, payment_type) VALUES (?, ?, NULL, ?, ?, ?)",
            (user_id, amount, f"Қарз төленди ({payment_type})", now, payment_type)
        )
        await db.execute("UPDATE Users SET total_debt = MAX(0, total_debt - ?) WHERE id = ?", (amount, user_id))
        await db.commit()

async def get_invoices_by_period(user_id: int, months: int):
    cutoff_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM Invoices WHERE user_id = ? AND date >= ? ORDER BY date DESC", 
            (user_id, cutoff_date)
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]

async def get_debtors_to_remind():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        query = '''
            SELECT DISTINCT u.id, u.total_debt 
            FROM Users u
            JOIN Invoices i ON u.id = i.user_id
            WHERE u.total_debt > 0 AND i.date <= ?
        '''
        async with db.execute(query, (ten_days_ago,)) as cursor:
            return [dict(row) for row in await cursor.fetchall()]

async def add_seller_to_db(user_id: int, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO StoreSellers (id, full_name) VALUES (?, ?)", (user_id, full_name))
        await db.commit()

async def remove_seller_from_db(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM StoreSellers WHERE id = ?", (user_id,))
        await db.commit()

async def get_all_sellers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM StoreSellers") as cursor:
            return [dict(row) for row in await cursor.fetchall()]

async def is_user_seller(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM StoreSellers WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def search_users_by_name(name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM Users WHERE full_name LIKE ?", (f"%{name}%",)) as cursor:
            return [dict(row) for row in await cursor.fetchall()]

def get_all_invoices_sync():
    import sqlite3
    from config import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Invoices ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_users_sync():
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]