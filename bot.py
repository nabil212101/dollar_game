import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_URL = "https://dollar-game.onrender.com"  # ضع رابط السيرفر الخاص بك هنا مع البورت إذا وجد، مثل http://localhost:5000

BOT_TOKEN = "7095959949:AAE3ujd3cazjhCj2sc0XcXLPKBP0dKVzwn4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # إرسال user_id إلى السيرفر لتسجيل الدخول
    try:
        response = requests.post(f"{API_URL}/api/login", json={"id": user_id})
        if response.status_code == 200:
            msg = "مرحبًا! تم تسجيل دخولك بنجاح.\n"
            msg += f"يمكنك الآن لعب اللعبة من خلال هذا الرابط:\n"
            msg += f"{API_URL}/game?user_id={user_id}"
        else:
            msg = "حدث خطأ أثناء تسجيل الدخول. حاول مرة أخرى لاحقًا."
    except Exception as e:
        msg = "تعذر الاتصال بالسيرفر. يرجى المحاولة لاحقًا."

    await update.message.reply_text(msg)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()
