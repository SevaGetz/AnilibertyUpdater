FROM python:3.11-slim

LABEL maintainer="AniLiberty Updater"
LABEL description="Automatic torrent updater for AniLiberty releases"

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование скрипта
COPY auto_update_torrents.py .

# Создание директорий
RUN mkdir -p temp_torrents

# Запуск
CMD ["python", "-u", "auto_update_torrents.py"]
