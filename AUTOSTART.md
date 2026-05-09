# Автозапуск

## Linux (systemd)

1. Отредактируйте `aniliberty-updater.service`:
   - Замените `%USER%` на ваше имя пользователя
   - Замените `%WORKING_DIR%` на полный путь к директории проекта

2. Скопируйте файл сервиса:
```bash
sudo cp aniliberty-updater.service /etc/systemd/system/
```

3. Включите и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aniliberty-updater
sudo systemctl start aniliberty-updater
```

4. Проверьте статус:
```bash
sudo systemctl status aniliberty-updater
```

5. Просмотр логов:
```bash
sudo journalctl -u aniliberty-updater -f
```

## Windows (Task Scheduler)

1. Откройте Task Scheduler (Планировщик заданий)

2. Создайте новую задачу:
   - Имя: "AniLiberty Updater"
   - Запускать независимо от входа пользователя в систему

3. Триггеры:
   - При запуске системы
   - Задержка: 1 минута

4. Действия:
   - Программа: `pythonw.exe`
   - Аргументы: `auto_update_torrents.py`
   - Рабочая папка: путь к проекту

5. Условия:
   - Запускать только при подключении к сети

6. Параметры:
   - При сбое перезапускать каждые: 1 минута
   - Число попыток перезапуска: 3

## Docker

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auto_update_torrents.py .
COPY config.json .

CMD ["python", "auto_update_torrents.py"]
```

Запуск:
```bash
docker build -t aniliberty-updater .
docker run -d --name aniliberty-updater \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/state.json:/app/state.json \
  aniliberty-updater
```

## Docker Compose

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  aniliberty-updater:
    build: .
    container_name: aniliberty-updater
    restart: unless-stopped
    volumes:
      - ./config.json:/app/config.json
      - ./state.json:/app/state.json
      - ./auto_update_torrents.log:/app/auto_update_torrents.log
    network_mode: host
```

Запуск:
```bash
docker-compose up -d
```
