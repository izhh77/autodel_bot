import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
user_settings = {}

async def autodelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user = update.message.from_user
    username = user.username.lower() if user.username else ""
    for uid, rules in user_settings.items():
        for rule_username, delay in rules:
            if username == rule_username:
                await context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id
                )

if __name__ == "__main__":
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("autodelete", autodelete))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_message))
    app.run_polling()
