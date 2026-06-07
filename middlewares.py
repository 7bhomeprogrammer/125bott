from aiogram import BaseMiddleware
from aiogram.types import Message
import database as db
import aiosqlite
from config import DB_PATH

class RoleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        username = event.from_user.username or "NoUsername"
        full_name = event.from_user.full_name
        
        # Используем INSERT OR IGNORE, чтобы не ловить ошибку при дубликатах
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                "INSERT OR IGNORE INTO Users (id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username, full_name)
            )
            await conn.commit()
        
        # Получаем актуальные данные из БД (через вашу функцию)
        user = await db.get_user_by_id(user_id)
        data['user'] = user  # Полезно передать данные пользователя дальше в хендлеры
        
        return await handler(event, data)