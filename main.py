import os
import time
import json
import threading
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OWNER_ID = 7811588898

# ضع معرّف قناتك الخاصة هنا لاحقًا
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

DATA_FILE = "aviator_data.json"
lock = threading.Lock()


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"results": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def send_message(chat_id, text):
    if not TOKEN or not chat_id:
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        return response.ok and response.json().get("ok", False)
    except requests.RequestException as error:
        print("Telegram send error:", error)
        return False


def notify_channel(text):
    if CHANNEL_ID:
        send_message(CHANNEL_ID, text)


@app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="ar" dir="rtl">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <body style="background:#101820;color:white;text-align:center;
    font-family:Arial;padding:30px">
    <h1>✈️ AVIATOR</h1>
    <p>الموقع يعمل بنجاح</p>
    <p>تحليل النتائج السابقة فقط، وليس التنبؤ بالجولات القادمة.</p>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def handle_message(message):
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user = message.get("from", {})
    user_id = user.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return

    # السماح للمالك فقط باستخدام أوامر الإدارة
    if user_id != OWNER_ID:
        send_message(
            chat_id,
            "🔒 هذا البوت خاص، ولا تملك صلاحية استخدام أوامر الإدارة."
        )
        return

    if text == "/start":
        reply = (
            "أهلًا بك في بوت AVIATOR ✈️\n\n"
            "أنت مالك البوت.\n"
            "استخدم /help لعرض الأوامر."
        )

    elif text == "/help":
        reply = (
            "📋 أوامر البوت:\n\n"
            "/start - تشغيل البوت\n"
            "/site - رابط الموقع\n"
            "/stats - إحصائيات النتائج المسجلة\n"
            "/help - المساعدة\n\n"
            "لا توجد ضمانات لنتائج الجولات القادمة."
        )

    elif text == "/site":
        reply = "🌐 رابط الموقع:\nhttps://aviator-yatb.onrender.com"

    elif text == "/stats":
        with lock:
            data = load_data()
            results = data.get("results", [])

        if not results:
            reply = (
                "📊 لا توجد نتائج مسجلة حتى الآن.\n"
                "لم يتم ربط مصدر تلقائي موثوق للنتائج بعد."
            )
        else:
            reply = (
                f"📊 عدد النتائج المسجلة: {len(results)}\n"
                "هذه إحصائيات تاريخية وليست توقعًا للجولة القادمة."
            )

    else:
        reply = "أرسل /help لرؤية الأوامر المتاحة."

    send_message(chat_id, reply)


def telegram_bot():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN is missing")
        return

    offset = 0

    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 25},
                timeout=35,
            )
            data = response.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # استقبال رسائل المحادثات الخاصة
                message = update.get("message")
                if message:
                    handle_message(message)

                # التقاط منشورات القناة التي يستطيع البوت رؤيتها
                channel_post = update.get("channel_post")
                if channel_post:
                    channel = channel_post.get("chat", {})
                    print("Channel detected:", channel.get("id"))

        except Exception as error:
            print("Telegram error:", error)
            time.sleep(5)


if __name__ == "__main__":
    threading.Thread(
        target=telegram_bot,
        daemon=True,
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )
