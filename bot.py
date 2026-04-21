import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH CỦA BẠN =================
TELEGRAM_BOT_TOKEN = '8386484128:AAHyzgK9kN8K-Iu6rFILWSlR2wp0iAHo_8Y'

# Danh sách 6 ID của ông giáo
ID_1 = 'EKDG-FU9L-LMYC'
ID_2 = 'FKAB-XTZL-LMGU'
ID_3 = 'SM8E-ZTHL-LMYC'
ID_4 = 'MMEH-HSHL-LMGG'
ID_5 = 'NMDA-HTHL-LMGG'
ID_6 = '9L6B-XS9L-LMGC'

GAME_IDS = [ID_1, ID_2, ID_3, ID_4, ID_5, ID_6] 

# ================= HÀM XỬ LÝ KẾT NỐI MẠNG (KEEP-ALIVE) =================
app = Flask('')

@app.route('/')
def home():
    return "Bot Play Together đang chạy ổn định!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# ================= HÀM XỬ LÝ BOT =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Chào ông giáo! Gửi giftcode vào đây, tui sẽ nạp cho cả 6 acc.')

async def handle_giftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giftcode = update.message.text.strip()
    danh_sach_id_chay = [uid for uid in GAME_IDS if uid != '']
    await update.message.reply_text(f'⏳ Đang cày mã: {giftcode} cho {len(danh_sach_id_chay)} tài khoản...')

    api_url = 'https://vgrapi-sea.vnggames.com/coordinator/api/v1/code/redeem' 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://giftcode.vnggames.com',
        'Referer': 'https://giftcode.vnggames.com/',
        'X-Client-Region': 'VN'
    }
    
    ket_qua_tong_hop = f"📊 **KẾT QUẢ MÃ {giftcode}:**\n\n"

    for idx, uid in enumerate(danh_sach_id_chay):
        payload = {
            "serverId": "2",
            "gameCode": "661",
            "roleId": uid,
            "roleName": uid,
            "code": giftcode
        }
        
        try:
            # Gửi request nạp code
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            # Cố gắng đọc JSON từ server bất kể mã HTTP là gì
            try:
                data = response.json()
            except:
                data = None
            
            # Trường hợp 1: Server báo thành công (200 OK và returnCode = 1)
            if response.status_code == 200 and data and str(data.get('returnCode')) == '1':
                ket_qua_tong_hop += f"✅ TK {idx + 1} ({uid}): Thành công\n"
            
            # Trường hợp 2: Server trả về lỗi (như Code đã dùng, Code sai...)
            elif data:
                # Bóc tách tin nhắn lỗi tiếng Việt/Anh từ VNG
                msg = data.get('message') or data.get('description') or data.get('returnMessage') or "Lỗi không xác định"
                ket_qua_tong_hop += f"❌ TK {idx + 1} ({uid}): {msg}\n"
            
            # Trường hợp 3: Lỗi kết nối server thật sự
            else:
                ket_qua_tong_hop += f"⚠️ TK {idx + 1} ({uid}): Lỗi hệ thống {response.status_code}\n"
                
        except Exception:
            ket_qua_tong_hop += f"🚨 TK {idx + 1} ({uid}): Lỗi mạng\n"
            
        # Nghỉ 1.5 giây mỗi acc cho chắc cú, tránh bị VNG khóa IP
        time.sleep(1.5)

    await update.message.reply_text(ket_qua_tong_hop, parse_mode='Markdown')

def main():
    # Bật web server để UptimeRobot có thể 'chọc' vào
    keep_alive()
    
    # Chạy bot Telegram
    app_bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giftcode))
    
    print("Bot đã sẵn sàng chiến đấu!")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
