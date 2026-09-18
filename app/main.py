import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from app.config import TELEGRAM_BOT_TOKEN, ADMIN_PASSWORD
from app.docker_client import (
    get_gateway_status, restart_gateway,
    stop_gateway, start_gateway, get_logs
)
from app.auth import sessions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Keyboards ───────────────────────────────────────────────────────

def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("📋 Logs", callback_data="logs")],
        [InlineKeyboardButton("🔄 Restart", callback_data="restart"),
         InlineKeyboardButton("🛑 Stop", callback_data="stop")],
        [InlineKeyboardButton("▶️ Start", callback_data="startgw"),
         InlineKeyboardButton("🔒 Logout", callback_data="logout")],
    ])

def cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Cancelar", callback_data="cancel")]
    ])

# ─── Helpers ─────────────────────────────────────────────────────────

async def send_menu(update: Update):
    await update.message.reply_text("Menu:", reply_markup=menu_keyboard())

def require_auth(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not sessions.is_authenticated(update.effective_user.id):
            await update.message.reply_text("🔒 No autenticado. Usa /start")
            return
        return await func(update, ctx)
    return wrapper

# ─── Auth handlers ─────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Envía el password:",
        reply_markup=cancel_keyboard()
    )
    ctx.user_data["awaiting_password"] = True

async def handle_password(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get("awaiting_password"):
        return
    ctx.user_data["awaiting_password"] = False
    if update.message.text == ADMIN_PASSWORD:
        sessions.authenticate(update.effective_user.id)
        await update.message.reply_text("✅ Acceso concedido!", reply_markup=menu_keyboard())
    else:
        await update.message.reply_text("❌ Password incorrecto. Usa /start para reintentar.")

async def cmd_logout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sessions.logout(update.effective_user.id)
    await update.message.reply_text("👋 Sesion cerrada.")

async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    await update.message.reply_text("Menu:", reply_markup=menu_keyboard())

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    s = get_gateway_status()
    health_emoji = "✅" if s.get("health") == "healthy" else "⚠️"
    status_emoji = "🟢" if s.get("running") else "🔴"
    uptime = s.get("uptime", "N/A")
    if uptime and uptime != "N/A":
        uptime = uptime.replace("T", " ").replace("Z", " UTC")
    await update.message.reply_text(
        f"{status_emoji} IB Gateway\n"
        f"Estado: {s.get('status', 'N/A')}\n"
        f"Salud: {health_emoji} {s.get('health', 'N/A')}\n"
        f"Uptime: {uptime}",
        reply_markup=menu_keyboard()
    )

async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    try:
        logs_text = get_logs(30)
        await update.message.reply_text(logs_text[:4096], reply_markup=menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

async def cmd_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    await update.message.reply_text("🔄 Reiniciando...")
    try:
        restart_gateway()
        await update.message.reply_text("✅ Gateway reiniciado", reply_markup=menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    await update.message.reply_text("🛑 Deteniendo...")
    try:
        stop_gateway()
        await update.message.reply_text("🛑 Gateway detenido", reply_markup=menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

async def cmd_startgw(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sessions.is_authenticated(update.effective_user.id):
        await update.message.reply_text("🔒 No autenticado. Usa /start")
        return
    await update.message.reply_text("▶️ Iniciando...")
    try:
        start_gateway()
        await update.message.reply_text("▶️ Gateway iniciado", reply_markup=menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

# ─── Callback (inline button press) ──────────────────────────────────

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not sessions.is_authenticated(user_id):
        await query.edit_message_text("🔒 No autenticado. Usa /start")
        return

    data = query.data

    if data == "status":
        s = get_gateway_status()
        health_emoji = "✅" if s.get("health") == "healthy" else "⚠️"
        status_emoji = "🟢" if s.get("running") else "🔴"
        uptime = s.get("uptime", "N/A")
        if uptime and uptime != "N/A":
            uptime = uptime.replace("T", " ").replace("Z", " UTC")
        text = (f"{status_emoji} IB Gateway\n"
                f"Estado: {s.get('status', 'N/A')}\n"
                f"Salud: {health_emoji} {s.get('health', 'N/A')}\n"
                f"Uptime: {uptime}")
        await query.edit_message_text(text, reply_markup=menu_keyboard())

    elif data == "logs":
        try:
            logs_text = get_logs(30)
            await query.edit_message_text(logs_text[:4096], reply_markup=menu_keyboard())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

    elif data == "restart":
        await query.edit_message_text("🔄 Reiniciando...")
        try:
            restart_gateway()
            await query.edit_message_text("✅ Gateway reiniciado", reply_markup=menu_keyboard())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

    elif data == "stop":
        await query.edit_message_text("🛑 Deteniendo...")
        try:
            stop_gateway()
            await query.edit_message_text("🛑 Gateway detenido", reply_markup=menu_keyboard())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

    elif data == "startgw":
        await query.edit_message_text("▶️ Iniciando...")
        try:
            start_gateway()
            await query.edit_message_text("▶️ Gateway iniciado", reply_markup=menu_keyboard())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=menu_keyboard())

    elif data == "logout":
        sessions.logout(user_id)
        await query.edit_message_text("👋 Sesion cerrada.")

    elif data == "cancel":
        ctx.user_data["awaiting_password"] = False
        await query.edit_message_text("Operacion cancelada.")

# ─── Main ─────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("startgw", cmd_startgw))
    app.add_handler(CommandHandler("logout", cmd_logout))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
