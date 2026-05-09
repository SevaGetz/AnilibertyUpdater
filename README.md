# Auto Update Torrents - AniLiberty

Автоматический скрипт для проверки новых серий на AniLiberty и обновления торрентов в qBittorrent Web API.

## Возможности

- Автоматическая проверка обновлений торрентов для отслеживаемых релизов
- Скачивание новых торрент-файлов через AniLiberty API
- Автоматическая замена старых торрентов на новые в qBittorrent
- Сохранение состояния между запусками
- Логирование всех операций
- Поддержка нескольких релизов одновременно

## Требования

- Python 3.7+
- qBittorrent с включенным Web UI
- Библиотека `requests`

## Установка

1. Установите зависимости:
```bash
pip install requests
```

2. Скопируйте пример конфигурации:
```bash
cp config.example.json config.json
```

3. Отредактируйте `config.json`:
   - Укажите URL и данные для входа в qBittorrent Web UI
   - Добавьте ID релизов, которые хотите отслеживать
   - Настройте интервал проверки (в секундах)

## Настройка qBittorrent

1. Откройте qBittorrent
2. Перейдите в Инструменты → Настройки → Web UI
3. Включите "Web User Interface (Remote control)"
4. Установите порт (по умолчанию 8080)
5. Задайте имя пользователя и пароль
6. Сохраните настройки

## Использование

### Добавить релиз в отслеживание

```bash
python auto_update_torrents.py --add-release 4754
```

### Выполнить одну проверку

```bash
python auto_update_torrents.py --once
```

### Запустить в режиме мониторинга

```bash
python auto_update_torrents.py
```

Скрипт будет проверять обновления с интервалом, указанным в конфигурации.

### Запуск в фоне (Linux/macOS)

```bash
nohup python auto_update_torrents.py > output.log 2>&1 &
```

### Запуск через systemd (Linux)

Создайте файл `/etc/systemd/system/aniliberty-updater.service`:

```ini
[Unit]
Description=AniLiberty Torrent Updater
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/AutoCheckAniliberty
ExecStart=/usr/bin/python3 /path/to/AutoCheckAniliberty/auto_update_torrents.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aniliberty-updater
sudo systemctl start aniliberty-updater
```

## Конфигурация

### config.json

```json
{
    "aniliberty": {
        "api_url": "https://aniliberty.top/api/v1",
        "check_interval": 300
    },
    "qbittorrent": {
        "url": "http://localhost:8080",
        "username": "admin",
        "password": "adminadmin"
    },
    "tracked_releases": [
        4754,
        5123
    ]
}
```

**Параметры:**

- `aniliberty.api_url` - URL API AniLiberty
- `aniliberty.check_interval` - Интервал проверки в секундах (по умолчанию 300 = 5 минут)
- `qbittorrent.url` - URL qBittorrent Web UI
- `qbittorrent.username` - Имя пользователя для входа
- `qbittorrent.password` - Пароль для входа
- `tracked_releases` - Массив ID релизов для отслеживания

## Как найти ID релиза

1. Откройте страницу релиза на AniLiberty
2. ID находится в URL: `https://aniliberty.top/release/4754` → ID = 4754

Или используйте API:
```bash
curl "https://aniliberty.top/api/v1/anime/catalog/releases?search=название"
```

## Логи

Все операции логируются в файл `auto_update_torrents.log` и выводятся в консоль.

## Файлы состояния

- `config.json` - Конфигурация приложения
- `state.json` - Текущее состояние отслеживаемых релизов (создается автоматически)
- `auto_update_torrents.log` - Лог-файл
- `temp_torrents/` - Временная директория для скачанных торрент-файлов

## Принцип работы

1. Скрипт периодически проверяет каждый релиз из списка через AniLiberty API
2. Получает список торрентов для релиза и выбирает самый свежий (по `updated_at`)
3. Сравнивает hash нового торрента с сохраненным в состоянии
4. Если hash отличается:
   - Скачивает новый торрент-файл
   - Удаляет старый торрент из qBittorrent (файлы остаются)
   - Добавляет новый торрент в qBittorrent
   - Обновляет состояние
5. qBittorrent автоматически продолжит скачивание с того места, где остановился

## Устранение неполадок

### Ошибка подключения к qBittorrent

- Проверьте, что qBittorrent запущен
- Проверьте URL и порт в конфигурации
- Убедитесь, что Web UI включен в настройках qBittorrent

### Ошибка авторизации

- Проверьте имя пользователя и пароль в конфигурации
- Убедитесь, что в qBittorrent не включена опция "Bypass authentication for clients on localhost"

### Торренты не обновляются

- Проверьте логи в `auto_update_torrents.log`
- Убедитесь, что ID релизов указаны правильно
- Проверьте доступность API AniLiberty

## Безопасность

- Не храните `config.json` в публичных репозиториях
- Используйте сильные пароли для qBittorrent Web UI
- Ограничьте доступ к Web UI только с localhost или доверенных IP

## Лицензия

MIT
