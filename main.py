import os
import time
import threading
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.route("/")
def home():
    return """
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
                timeout=35
            )
            data = response.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "").strip()

                if not chat_id or not text:
                    continue

                if text == "/start":
                    reply = (
                        "أهلًا بك في بوت AVIATOR ✈️\n\n"
                        "البوت يعمل الآن.\n"
                        "أرسل /help لمعرفة الأوامر."
                    )
                elif text == "/help":
                    reply = (
                        "الأوامر المتاحة:\n"
                        "/start - تشغيل البوت\n"
                        "/site - رابط الموقع\n"
                        "/help - المساعدة\n\n"
                        "لا يمكن ضمان نتيجة الجولة القادمة."
                    )
                elif text == "/site":
                    reply = "رابط الموقع:\nhttps://aviator-yatb.onrender.com"
                else:
                    reply = "أرسل /help لرؤية الأوامر المتاحة."

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": reply},
                    timeout=10
                )

        except Exception as error:
            print("Telegram error:", error)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(
        target=telegram_bot,
        daemon=True
    ).start()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
