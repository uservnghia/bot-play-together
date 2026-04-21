import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH CỦA BẠN =================
# CẢNH BÁO BẢO MẬT: Token này là chìa khóa điều khiển bot của bạn. 
# Tui giữ nguyên ở đây để bạn dễ copy, nhưng tuyệt đối đừng gửi file này cho ai khác nhé.
TELEGRAM_BOT_TOKEN = '8386484128:AAHyzgK9kN8K-Iu6rFILWSlR2wp0iAHo_8Y'

# Tách riêng các ID để dễ quản lý
ID_1 = 'EKDG-FU9L-LMYC'
ID_2 = 'FKAB-XTZL-LMGU'

# Đưa các ID muốn chạy vào danh sách này
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

# ================= HÀM XỬ LÝ BOT =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Chào bạn! Gửi giftcode vào đây nhé.')

async def handle_giftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giftcode = update.message.text.strip()
    danh_sach_id_chay = [uid for uid in GAME_IDS if uid != '']
    await update.message.reply_text(f'⏳ Đang nhập mã: {giftcode}...')

    api_url = 'https://vgrapi-sea.vnggames.com/coordinator/api/v1/code/redeem' 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json'
    }
    
    ket_qua_tong_hop = f"📊 **Kết quả mã {giftcode}:**\n\n"

    for idx, uid in enumerate(danh_sach_id_chay):
        # Tách biệt rõ ràng từng tham số vào payload theo đúng F12
        payload = {
            "serverId": "2",
            "gameCode": "661",
            "roleId": uid,
            "roleName": uid,
            "code": giftcode
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Bắt lỗi theo định dạng JSON trả về của VNG
                if data.get('status') == 'success' or str(data.get('returnCode')) == '1':
                    ket_qua_tong_hop += f"✅ TK {idx + 1} ({uid}): Thành công\n"
                else:
                    loi = data.get('message') or data.get('returnMessage') or str(data)
                    ket_qua_tong_hop += f"❌ TK {idx + 1} ({uid}): {loi}\n"
            else:
                ket_qua_tong_hop += f"⚠️ TK {idx + 1} ({uid}): Máy chủ từ chối (Lỗi HTTP {response.status_code})\n"
                
        except Exception as e:
            ket_qua_tong_hop += f"🚨 TK {idx + 1} ({uid}): Lỗi mạng (Không kết nối được VNG)\n"
            
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
