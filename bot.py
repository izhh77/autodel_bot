import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from datetime import datetime, timedelta

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

API_TOKEN = os.getenv("API_TOKEN")

# Simpan setting pengguna
user_settings = {}

# /autodelete <username> <seconds>
async def autodelete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Guna format: /autodelete <username> <seconds>")
        return

    username, seconds = context.args
    try:
        seconds = int(seconds)
    except ValueError:
        await update.message.reply_text("Masukkan nilai saat yang sah.")
        return

    user_id = update.effective_user.id
    if user_id not in user_settings:
        user_settings[user_id] = []

    user_settings[user_id].append((username.lower(), seconds))
    await update.message.reply_text(f"Auto-delete mesej dari @{username} dalam {seconds}s.")

# Handle mesej dalam group
async def delete_target_bot_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    username = user.username.lower() if user.username else ""
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    for uid, rules in user_settings.items():
        for rule_username, delay in rules:
            if username == rule_username:
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"Mesej dari @{username} akan dipadam dalam {delay} saat."
                    )
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=message_id
                    )
                except Exception as e:
                    logging.warning(f"Gagal padam mesej: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("autodelete", autodelete_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_target_bot_messages))

    print("Bot started")
    app.run_p_
