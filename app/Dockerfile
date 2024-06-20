# Используем официальный образ Python 3.10 slim
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей requirements.txt из корневой директории в контейнер
COPY requirements.txt .
# Установка git
RUN apt-get update && \
    apt-get install -y git
# Устанавливаем зависимости из requirements.txt
RUN pip install -r requirements.txt

# Копируем скрипт plot_single.py из директории scripts в рабочую директорию контейнера
COPY scripts/plot_single.py .

# Команда по умолчанию при запуске контейнера
CMD ["python", "plot_single.py"]
