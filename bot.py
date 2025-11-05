import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# состояния диалога
GENDER, AGE, HEIGHT, WEIGHT, ACTIVITY = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Мужчина")], [KeyboardButton("Женщина")]]
    await update.message.reply_text(
        "Привет! 👋 Я помогу рассчитать твое КБЖУ.\nВыбери пол:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data["gender"] = text
    await update.message.reply_text("Введите возраст (в годах):")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["age"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целое число для возраста.")
        return AGE
    await update.message.reply_text("Введите рост (в см):")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["height"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи рост в сантиметрах (число).")
        return HEIGHT
    await update.message.reply_text("Введите вес (в кг):")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["weight"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи вес в килограммах (например 68.5).")
        return WEIGHT

    keyboard = [
        [KeyboardButton("1.2 — минимальная активность")],
        [KeyboardButton("1.375 — лёгкая активность")],
        [KeyboardButton("1.55 — средняя активность")],
        [KeyboardButton("1.725 — высокая активность")],
        [KeyboardButton("1.9 — очень высокая активность")],
    ]
    await update.message.reply_text(
        "Выберите уровень активности:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        activity_val = float(text.split(" — ")[0].strip())
    except Exception:
        await update.message.reply_text("Пожалуйста, выбери уровень активности кнопкой.")
        return ACTIVITY

    data = context.user_data
    gender = data.get("gender", "мужчина").lower()
    weight = data["weight"]
    height = data["height"]
    age = data["age"]

    # Миффлин — Сан Жеор
    if gender.startswith("м"):
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity_val
    proteins = (tdee * 0.3) / 4
    fats = (tdee * 0.3) / 9
    carbs = (tdee * 0.4) / 4

    text_out = (
        f"✨ Твоя норма:\n"
        f"🔥 Калории: {tdee:.0f} ккал/день\n"
        f"🍗 Белки: {proteins:.0f} г\n"
        f"🥑 Жиры: {fats:.0f} г\n"
        f"🍞 Углеводы: {carbs:.0f} г\n\n"
        f"Хочешь получить персональные рекомендации по питанию и тренировкам?"
    )
    keyboard = [
        [InlineKeyboardButton("Получить рекомендации (платно)", callback_data="buy_recommendations")]
    ]
    await update.message.reply_text(text_out, reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        if query.data == "buy_recommendations":
            await query.edit_message_text(
                "Рекомендации доступны после оплаты. Для теста можно оплатить на сайте или связаться со мной."
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /start чтобы запустить калькулятор КБЖУ.")

def main():
    TOKEN = os.getenv("TOKEN")  # убедись, что в Render переменная называется TOKEN
    if not TOKEN:
        raise RuntimeError("Переменная окружения TOKEN не задана. Проверь Environment Variables в Render.")

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity)],
        },
        fallbacks=[CommandHandler("help", help_command)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, lambda u,c: None))  # заглушка
    app.add_handler(MessageHandler(filters.Regex("^/"), help_command))  # на всякий случай
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, lambda u,c: None))
    app.add_handler(MessageHandler(filters.Regex(".*"), lambda u,c: None))
    # обработчик inline-кнопок
    app.add_handler(CommandHandler("premium", help_command))
    app.add_handler(MessageHandler(filters.ALL, lambda u,c: None))
    app.add_handler(MessageHandler(filters.ALL, lambda u,c: None))
    # callback
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ Бот запущен (run_polling).")
    app.run_polling()

if __name__ == "__main__":
    main()
