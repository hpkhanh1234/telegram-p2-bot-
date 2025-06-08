import os

os.system("pip install pandas openpyxl flask python-telegram-bot==20.6")
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import difflib
from flask import Flask
from threading import Thread
import os

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
        answer = str(row.iloc[1]).replace('\\n', '\n') if pd.notna(
            row.iloc[1]) else "Chưa có đáp án cho câu hỏi này"
        qa_dict[question] = answer
    print(f"✅ Đã nạp {len(qa_dict)} câu hỏi từ {EXCEL_FILE}")


# ==========================
# 4. Các hàm xử lý bot
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '✅ Xin chào! Tôi là bot thi P2. Bạn có thể gửi câu hỏi để tôi tìm đáp án.'
    )


async def handle_message(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_question = normalize_spaces(update.message.text)
    normalized_qa_dict = {normalize_spaces(q): q for q in qa_dict.keys()}
    closest_match = difflib.get_close_matches(user_question,
                                              normalized_qa_dict.keys(),
                                              n=1,
                                              cutoff=0.1)

    if closest_match:
        matched_key = normalized_qa_dict[closest_match[0]]
        answer = qa_dict.get(matched_key, "Chưa có đáp án cho câu hỏi này")
    else:
        answer = "❌ Tôi không tìm thấy câu hỏi phù hợp."

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
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot đã khởi động...")
    application.run_polling()


if __name__ == '__main__':
    main()
