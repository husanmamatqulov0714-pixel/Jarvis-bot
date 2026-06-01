#!/usr/bin/env python3
"""
J.A.R.V.I.S. Telegram Bot
Mualif: Mamatqulov Husan
© 2025 Mamatqulov Husan. Barcha huquqlar himoyalangan.
"""

import asyncio
import json
import os
import urllib.request
import urllib.parse
import urllib.error

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8837371558:AAGC9hhcp-8hFV6VYvBOSghUMU2f0Eh7uzw")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "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")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

SYSTEM_PROMPT = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), created by Mamatqulov Husan. You are a highly intelligent AI assistant inspired by Iron Man's AI. Respond in whatever language the user writes in. Be professional, helpful, and slightly formal. Use phrases like "Certainly", "Of course", "Right away" occasionally."""

# Store conversation history per user
user_histories = {}

def telegram_request(method, data=None):
    url = f"{API_URL}/{method}"
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Telegram error: {e}")
        return None

def ask_openrouter(user_id, message):
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    user_histories[user_id].append({"role": "user", "content": message})
    
    # Keep last 20 messages
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[user_id]
    
    payload = json.dumps({
        "model": "google/gemma-3-4b-it:free",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "HTTP-Referer": "https://t.me/jarvis_bot",
            "X-Title": "JARVIS"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            reply = data['choices'][0]['message']['content']
            user_histories[user_id].append({"role": "assistant", "content": reply})
            return reply
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

def send_message(chat_id, text, parse_mode="Markdown"):
    # Split long messages
    if len(text) > 4000:
        text = text[:4000] + "..."
    
    telegram_request("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    })

def send_typing(chat_id):
    telegram_request("sendChatAction", {
        "chat_id": chat_id,
        "action": "typing"
    })

def handle_update(update):
    if "message" not in update:
        return
    
    message = update["message"]
    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    user_name = message["from"].get("first_name", "Janob")
    text = message.get("text", "")
    
    if not text:
        return
    
    print(f"[{user_name}]: {text}")
    
    # Commands
    if text == "/start":
        welcome = f"""🤖 *J.A.R.V.I.S.* ga xush kelibsiz, {user_name}!

*Just A Rather Very Intelligent System*

Men sizning aqlli yordamchingizman. Istalgan savolingizni bering!

👨‍💻 *Mualif:* Mamatqulov Husan
📌 *Versiya:* 1.0.0

_Buyrug'ingizni bering, janob._"""
        send_message(chat_id, welcome)
        return
    
    if text == "/clear":
        user_histories[user_id] = []
        send_message(chat_id, "✅ Suhbat tarixi tozalandi.")
        return
    
    if text == "/help":
        help_text = """*J.A.R.V.I.S. Buyruqlar:*

/start — Botni boshlash
/clear — Suhbat tarixini tozalash  
/help — Yordam

Istalgan xabar yozing — javob beraman! 🤖"""
        send_message(chat_id, help_text)
        return
    
    # Show typing
    send_typing(chat_id)
    
    # Get AI response
    reply = ask_openrouter(user_id, text)
    send_message(chat_id, reply)
    print(f"[JARVIS]: {reply[:100]}...")

def main():
    print("🤖 J.A.R.V.I.S. Bot ishga tushdi!")
    print("Mualif: Mamatqulov Husan")
    print("Toxtatish uchun: Ctrl+C")
    
    offset = 0
    while True:
        try:
            result = telegram_request("getUpdates", {
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message"]
            })
            
            if result and result.get("ok") and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1
                    handle_update(update)
        except KeyboardInterrupt:
            print("\nBot toxtatildi.")
            break
        except Exception as e:
            print(f"Xato: {e}")
            import time
            time.sleep(5)

if __name__ == "__main__":
    main()
