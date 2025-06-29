import os

os.system("pip install pandas openpyxl flask python-telegram-bot==20.6")
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ==========================
# 1. Khởi tạo web server để giữ Replit không bị ngủ
# ==========================
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy trên Replit!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()

# ==========================
# 2. Hàm chuẩn hóa khoảng trắng
# ==========================
def normalize_spaces(text: str) -> str:
    return ' '.join(text.strip().split())

# ==========================
# 3. Đọc dữ liệu Excel vào qa_dict
# ==========================
qa_dict = {}
EXCEL_FILE = "input_Thi_P2.xlsx"

if not os.path.exists(EXCEL_FILE):
    print(f"⚠️ Không tìm thấy file {EXCEL_FILE}")
else:
    df = pd.read_excel(EXCEL_FILE)
    for index, row in df.iterrows():
        question = str(row.iloc[0]).replace('\\n', '\n')
        answer = str(row.iloc[1]).replace('\\n', '\n') if pd.notna(row.iloc[1]) else "Chưa có đáp án cho câu hỏi này"
        qa_dict[question] = answer
    print(f"✅ Đã nạp {len(qa_dict)} câu hỏi từ {EXCEL_FILE}")

# ==========================
# 4. Các hàm xử lý bot
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '✅ Xin chào! Tôi là bot thi P2. Bạn có thể gửi câu hỏi để tôi tìm đáp án.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_question = normalize_spaces(update.message.text).lower()
    matched_question = None

    for question in qa_dict.keys():
        normalized_question = normalize_spaces(question).lower()
        if user_question in normalized_question:  # Like "%xxxx%"
            matched_question = question
            break

    if matched_question:
        answer = qa_dict.get(matched_question, "Chưa có đáp án cho câu hỏi này")
    else:
        answer = "❌ Câu hỏi không có trong kho dữ liệu."

    await update.message.reply_text(answer)

# ==========================
# 5. Khởi tạo bot và polling
# ==========================
def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("❌ Chưa cấu hình biến môi trường BOT_TOKEN")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot đã khởi động...")
    application.run_polling()

if __name__ == '__main__':
    main()
