# Используем стабильную версию Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем переменную окружения для токена
ENV BOT_TOKEN=${BOT_TOKEN}

# Запуск бота
CMD ["python", "bot.py"]
