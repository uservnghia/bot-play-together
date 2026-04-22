import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH CỦA BẠN =================
TELEGRAM_BOT_TOKEN = '8386484128:AAHyzgK9kN8K-Iu6rFILWSlR2wp0iAHo_8Y'

# Tách riêng các ID để dễ quản lý
ID_1 = 'NMDA-HTHL-LMGG'
ID_2 = 'MMEH-HSHL-LMGG'

# Đưa các ID muốn chạy vào danh sách này
GAME_IDS = [ID_1, ID_2] 

# ================= HÀM XỬ LÝ KẾT NỐI MẠNG (KEEP-ALIVE) =================
app = Flask('')

@app.route('/')
def home():
    return "Bot đang sống nhăn răng!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://giftcode.vnggames.com',
        'Referer': 'https://giftcode.vnggames.com/',
        'X-Client-Region': 'VN',
        'Dnt': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }
    
    ket_qua_tong_hop = f"📊 **Kết quả mã {giftcode}:**\n\n"

    for idx, uid in enumerate(danh_sach_id_chay):
        # PAYLOAD: Đã trả lại dạng Chuỗi (có dấu nháy)
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
                
                if str(data.get('returnCode')) == '1':
                    ket_qua_tong_hop += f"✅ TK {idx + 1} ({uid}): Thành công\n"
                else:
                    thong_bao = data.get('returnMessage') or data.get('message') or "Lỗi không xác định"
                    ket_qua_tong_hop += f"❌ TK {idx + 1} ({uid}): {thong_bao}\n"
            else:
                # IN THẲNG LÝ DO SERVER TỪ CHỐI RA TELEGRAM (Chiêu gỡ lỗi cuối cùng)
                loi_chi_tiet = response.text 
                ket_qua_tong_hop += f"⚠️ TK {idx + 1} ({uid}): Lỗi {response.status_code} - {loi_chi_tiet}\n"
                
        except Exception as e:
            ket_qua_tong_hop += f"🚨 TK {idx + 1} ({uid}): Lỗi kết nối\n"
            
        time.sleep(1)

    await update.message.reply_text(ket_qua_tong_hop, parse_mode='Markdown')

def main():
    keep_alive()
    app_bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giftcode))
    
    print("Bot đang chạy...")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
