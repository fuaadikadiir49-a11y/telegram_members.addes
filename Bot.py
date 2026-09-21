import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("8662593320:AAHnZ6wdKjYAzGqiRG6XReqwhuYVSFK68rk")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it in .env")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Akkam! 👋\n\n"
        "Botichi namni ofii isaatiin groupitti seenuuf link argachuuf fayyada.\n"
        "/join - Linkii groupii argachuuf\n"
        "/help - Gargaarsa"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Bot jalqabi\n"
        "/join - Linkii groupii gaafadhu\n"
        "/help - Gargaarsa"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set your group invite link in .env as GROUP_INVITE_LINK
    link = os.getenv("GROUP_INVITE_LINK")
    if not link:
        await update.message.reply_text(
            "GROUP_INVITE_LINK .env keessatti hin kaa'amne."
        )
        return

    await update.message.reply_text(
        f"Groupii seenuuf link kana cuqaasi:\n{link}"
    )

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("join", join))

    print("Telegram bot started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

