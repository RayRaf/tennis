# Указываем базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости для системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта в контейнер
COPY . .

# Выполняем сбор статики
RUN python manage.py collectstatic --noinput

# Открываем порт для приложения
EXPOSE 8000

# Устанавливаем команду запуска приложения
CMD ["sh", "-c", "python manage.py migrate && uvicorn tennis.asgi:application --host 0.0.0.0 --port 8000"]