from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from fpdf import FPDF

# Состояния для диалога
CHOOSING, TYPING_REPLY = range(2)

# Данные, которые заполняет пользователь
user_data = {}

# Функция генерации PDF
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Устанавливаем шрифт, который поддерживает Unicode
    pdf.add_font('arial', '', 'arial.ttf', uni=True)  # Убедитесь, что файл шрифта находится в той же папке
    pdf.set_font('arial', size=12)
    
    pdf.cell(200, 10, txt="Накладная", ln=True, align='C')
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    filename = "invoice.pdf"
    pdf.output(filename)
    return filename

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Добро пожаловать! Давайте создадим накладную.\n"
        "Введите параметр (например, 'Имя клиента'), или напишите 'готово', чтобы завершить."
    )
    return CHOOSING

# Обработка выбора параметра
async def received_information(update: Update, context: CallbackContext):
    text = update.message.text

    if text.lower() == "готово":
        if user_data:
            await update.message.reply_text("Генерирую PDF...")
            pdf_file = generate_pdf(user_data)
            with open(pdf_file, "rb") as f:
                await update.message.reply_document(document=f)
            user_data.clear()
        else:
            await update.message.reply_text("Вы не ввели данные.")
        return ConversationHandler.END

    context.user_data["key"] = text
    await update.message.reply_text(f"Теперь введите значение для '{text}':")
    return TYPING_REPLY

# Обработка ввода значения
async def save_data(update: Update, context: CallbackContext):
    key = context.user_data["key"]
    value = update.message.text
    user_data[key] = value
    await update.message.reply_text(f"Сохранено: {key} = {value}\nВведите следующий параметр или 'готово' для завершения.")
    return CHOOSING

# Завершение диалога
async def cancel(update: Update, context: CallbackContext):
    user_data.clear()
    await update.message.reply_text("Создание накладной отменено.")
    return ConversationHandler.END

# Основная функция
def main():
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("").build()

    # Диалоговое взаимодействие
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_information)],
            TYPING_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
