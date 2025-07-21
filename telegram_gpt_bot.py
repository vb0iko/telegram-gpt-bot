import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
import os
import fitz  # PyMuPDF
import tempfile
from gtts import gTTS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
user_contexts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я GPT-бот. Надішли текст, PDF або голос — і я відповім!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    if user_id not in user_contexts:
        user_contexts[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    user_contexts[user_id].append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=user_contexts[user_id],
        temperature=0.7
    )
    reply = response.choices[0].message.content
    user_contexts[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        await file.download_to_drive(custom_path=tf.name)
        doc = fitz.open(tf.name)
        text = ""
        for page in doc:
            text += page.get_text()
        await update.message.reply_text("📄 PDF прочитано. Відповідаю...")
        update.message.text = text
        await handle_text(update, context)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()
    await update.message.reply_text("🎤 Отримав голос! (розпізнавання не реалізовано, оброблю як є)")
    await update.message.reply_text("⛔️ Поки що голос тільки відправляється у відповідь як звук.")
    tts = gTTS("Це тестова відповідь бота голосом.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        with open(tmp.name, "rb") as audio:
            await update.message.reply_voice(audio)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))

if __name__ == "__main__":
    app.run_polling()
