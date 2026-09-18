import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

import telebot

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Set BOT_TOKEN as an environment variable before starting the bot.")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

PROJECT_DIR = Path(__file__).resolve().parent / "android_project"
JAVA_PATH = PROJECT_DIR / "app/src/main/java/com/darktunnel/app/MainActivity.java"
APK_PATH = PROJECT_DIR / "app/build/outputs/apk/debug/app-debug.apk"

BUILD_LOCK = threading.Lock()


@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(
        message,
        "👋 Nagaan dhuftan! Ergaa kana booda MainActivity.java kee naaf ergi. "
        "Ani project Android keessatti kaa'ee debug APK ijaara."
    )


@bot.message_handler(content_types=["document"])
def handle_document(message):
    name = message.document.file_name or ""
    if not (name.endswith(".java") or name.endswith(".txt")):
        bot.reply_to(message, "⚠️ Faayilii .java ykn .txt qofa ergi.")
        return

    if not BUILD_LOCK.acquire(blocking=False):
        bot.reply_to(message, "⏳ Build biraa deemaa jira. Mee yeroo muraasa booda yaali.")
        return

    threading.Thread(
        target=build_for_user,
        args=(message.chat.id, message.document.file_id),
        daemon=True,
    ).start()


def build_for_user(chat_id, file_id):
    try:
        bot.send_message(chat_id, "📥 Faayilii fudhadhe. Build qopheessaa jira...")

        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        # Keep the Android project structure fixed. The uploaded file only
        # replaces MainActivity.java; it cannot modify Gradle/build files.
        JAVA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)

        try:
            JAVA_PATH.write_bytes(tmp_path.read_bytes())
        finally:
            tmp_path.unlink(missing_ok=True)

        # Use an installed Gradle command. Android SDK/JDK/Gradle must exist
        # on the machine running this bot.
        result = subprocess.run(
            ["gradle", "assembleDebug", "--no-daemon"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            error = (result.stderr or result.stdout)[-2500:]
            bot.send_message(
                chat_id,
                "❌ Build hin milkoofne.\n<pre>" +
                escape_html(error) +
                "</pre>",
            )
            return

        if not APK_PATH.exists():
            bot.send_message(chat_id, "❌ Build milkaa'e fakkaata, garuu APK hin argamne.")
            return

        with APK_PATH.open("rb") as apk:
            bot.send_document(
                chat_id,
                apk,
                caption="✅ APK debug kee qophaa'eera.",
            )

    except subprocess.TimeoutExpired:
        bot.send_message(chat_id, "⏱️ Build daqiiqaa 10 caale; hojii dhaabbate.")
    except Exception as exc:
        bot.send_message(chat_id, f"❌ Rakkoo uumame: {exc}")
    finally:
        BUILD_LOCK.release()


def escape_html(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
