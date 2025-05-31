from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7095959949:AAE3ujd3cazjhCj2sc0XcXLPKBP0dKVzwn4"

# لاحقًا غيّر الرابط لو رفعت الموقع على الإنترنت
GAME_BASE_URL = "http://127.0.0.1:5000/game?user_id="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    game_link = GAME_BASE_URL + str(user_id)

    message = f"مرحباً {full_name} 👋\n" \
              f"اضغط على الرابط التالي لبدء اللعبة وكسب دولار يومياً:\n\n" \
              f"{game_link}"

    await update.message.reply_text(message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running... اضغط Ctrl+C للإيقاف.")
    app.run_polling()
