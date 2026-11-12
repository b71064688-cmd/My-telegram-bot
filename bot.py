import os
import telebot
import requests

# قراءة التوكن والمفتاح من إعدادات البيئة أو وضعها مباشرة هنا
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '7727783062:AAFBivQ3o1_gAl5wTyU-KEmDLTdjjhsTZ9U')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! اكتب كلمة 'مساعد' لكي أبدأ الرد عليك، أو قم بالرد على أي رسالة لي.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text if message.text else ""
    
    is_help = "مساعد" in text
    is_reply_to_bot = False
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        is_reply_to_bot = True

    if not (is_help or is_reply_to_bot):
        return

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        models_url = "https://api.groq.com/openai/v1/models"
        models_res = requests.get(models_url, headers=headers).json()
        
        target_model = "llama-3.1-8b-instant"
        if "data" in models_res:
            for m in models_res["data"]:
                m_id = m["id"].lower()
                if any(name in m_id for name in ["llama", "gemma", "mixtral", "qwen"]):
                    if not any(bad in m_id for bad in ["whisper", "orpheus", "embed", "audio", "vision", "rt", "guard", "classifier", "prompt-guard"]):
                        target_model = m["id"]
                        break

        url = "https://api.groq.com/openai/v1/chat/completions"
        data = {
            "model": target_model,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": "أنت مساعد ذكي تجيب باللغة العربية بشكل مختصر ومفيد."},
                {"role": "user", "content": text}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if "choices" in result:
            reply = result['choices'][0]['message']['content']
            bot.reply_to(message, reply)
        else:
            error_msg = result.get('error', {}).get('message', 'خطأ غير معروف')
            bot.reply_to(message, f"عذراً، رد الخادم: {error_msg}")
            
    except Exception as e:
        print("❌ حدث خطأ مفصل:", e)
        bot.reply_to(message, f"خطأ تقني: {e}")

bot.infinity_polling()

