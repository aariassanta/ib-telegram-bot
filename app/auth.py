from datetime import datetime, timedelta
from typing import Optional

class AuthSession:
    def __init__(self):
        self.authenticated_users: dict[int, datetime] = {}

    def authenticate(self, user_id: int) -> None:
        self.authenticated_users[user_id] = datetime.now() + timedelta(hours=24)

    def is_authenticated(self, user_id: int) -> bool:
        exp = self.authenticated_users.get(user_id)
        return exp is not None and datetime.now() < exp

    def logout(self, user_id: int) -> None:
        self.authenticated_users.pop(user_id, None)

sessions = AuthSession()

def require_auth(func):
    async def wrapper(update, ctx):
        from app.config import AUTHORIZED_USER_IDS_SET
        user_id = update.effective_user.id
        # If authorized user IDs are configured, check first
        if AUTHORIZED_USER_IDS_SET and user_id not in AUTHORIZED_USER_IDS_SET:
            await update.message.reply_text("❌ No estás autorizado.")
            return
        if not sessions.is_authenticated(user_id):
            await update.message.reply_text("🔒 No autenticado. Usa /start")
            return
        return await func(update, ctx)
    return wrapper
