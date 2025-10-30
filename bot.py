import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

GENDER, AGE, HEIGHT, WEIGHT, ACTIVITY = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Мужчина")], [KeyboardButton("Женщина")]]
    await update.message.reply_text(
        "Привет! 👋 Я помогу рассчитать твое КБЖУ.\nВыбери пол:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text.lower()
    await update.message.reply_text("Введите возраст:")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = int(update.message.text)
    await update.message.reply_text("Введите рост (см):")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = int(update.message.text)
    await update.message.reply_text("Введите вес (кг):")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = float(update.message.text)
    keyboard = [
        [KeyboardButton("1.2 — минимальная активность")],
        [KeyboardButton("1.375 — лёгкая активность")],
        [KeyboardButton("1.55 — средняя активность")],
        [KeyboardButton("1.725 — высокая активность")],
        [KeyboardButton("1.9 — очень высокая активность")]
    ]
    await update.message.reply_text(
        "Выберите уровень активности:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity_str = update.message.text.split(" — ")[0]
    activity = float(activity_str)
    data = context.user_data

    if data["gender"].startswith("м"):
        bmr = 10 * data["weight"] + 6.25 * data["height"] - 5 * data["age"] + 5
    else:
        bmr = 10 * data["weight"] + 6.25 * data["height"] - 5 * data["age"] - 161

    tdee = bmr * activity
    proteins = (tdee * 0.3) / 4
    fats = (tdee * 0.3) / 9
    carbs = (tdee * 0.4) / 4

    await update.message.reply_text(
        f"✨ Твоя норма:\n"
        f"Калории: {tdee:.0f} ккал\n"
        f"Белки: {proteins:.0f} г\n"
        f"Жиры: {fats:.0f} г\n"
        f"Углеводы: {carbs:.0f} г\n\n"
        f"🚀 Хочешь получить персональные рекомендации по питанию и тренировкам?\n"
        f"Это доступно в премиум-версии. Напиши /premium"
    )
    return ConversationHandler.END

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 Premium доступ:\n"
        "— Индивидуальные советы по питанию\n"
        "— Пример меню\n"
        "— Рекомендации по БЖУ под цель (похудение/набор)\n\n"
        "Стоимость: 499₽\n"
        "Для активации напиши: @твоё_имя (или добавь оплату позже через Telegram Payments)"
    )

TOKEN = os.getenv("TOKEN")
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
    fallbacks=[]
)

app.add_handler(conv)
app.add_handler(CommandHandler("premium", premium))
app.run_polling()
