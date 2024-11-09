# Используем последний образ Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /fastapi_app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
#RUN #pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Копируем всё содержимое текущей директории в контейнер
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение с использованием uvicorn
CMD ["uvicorn", "app.main:app",  "--host", "0.0.0.0", "--port", "8000"]
