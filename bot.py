import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH CỦA BẠN =================
TELEGRAM_BOT_TOKEN = '8386484128:AAHyzgK9kN8K-Iu6rFILWSlR2wp0iAHo_8Y'

# Tách riêng các ID để dễ quản lý, bạn điền ID vào trong dấu nháy đơn
ID_1 = 'EKDG-FU9L-LMYC'
ID_2 = 'FKAB-XTZL-LMGU'

# Đưa các ID muốn chạy vào danh sách này (ví dụ đang để chạy 3 ID)
GAME_IDS = [ID_1, ID_2] 

# ================= HÀM XỬ LÝ KẾT NỐI MẠNG (KEEP-ALIVE) =================
app = Flask('')

@app.route('/')
def home():
    return "Bot đang sống nhăn răng!"

def run_server():
    # Chạy server web trên cổng 8080
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Tạo một luồng (thread) chạy ngầm server web để không chặn luồng của Bot
    t = Thread(target=run_server)
    t.start()

# ================= HÀM XỬ LÝ BOT (Giữ nguyên như cũ) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Chào bạn! Gửi giftcode vào đây nhé.')

async def handle_giftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giftcode = update.message.text.strip()
    danh_sach_id_chay = [uid for uid in GAME_IDS if uid != '']
    await update.message.reply_text(f'⏳ Đang nhập mã: {giftcode}...')

    api_url = 'https://api-coupon.playtogether.com/v1/redeem' 
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    }
    ket_qua_tong_hop = f"📊 **Kết quả mã {giftcode}:**\n\n"

    for idx, uid in enumerate(danh_sach_id_chay):
        payload = {'game_id': uid, 'code': giftcode}
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    ket_qua_tong_hop += f"✅ TK {idx + 1} ({uid}): Thành công\n"
                else:
                    ket_qua_tong_hop += f"❌ TK {idx + 1} ({uid}): {data.get('message', 'Lỗi')}\n"
            else:
                ket_qua_tong_hop += f"⚠️ TK {idx + 1} ({uid}): Máy chủ từ chối\n"
        except Exception as e:
            ket_qua_tong_hop += f"🚨 TK {idx + 1} ({uid}): Lỗi mạng\n"
        time.sleep(1)

    await update.message.reply_text(ket_qua_tong_hop, parse_mode='Markdown')

def main():
    # 1. Bật web server ngầm trước
    keep_alive()
    
    # 2. Chạy bot
    app_bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giftcode))
    print("Bot đã chạy...")
    app_bot.run_polling()

if __name__ == '__main__':
    main()