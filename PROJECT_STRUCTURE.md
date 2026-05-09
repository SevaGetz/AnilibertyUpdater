# Структура проекта

```
AutoCheckAniliberty/
├── auto_update_torrents.py      # Основной скрипт
├── requirements.txt              # Python зависимости
├── config.example.json           # Пример конфигурации
├── config.json                   # Конфигурация (создается при установке)
├── state.json                    # Состояние (создается автоматически)
├── manage.sh                     # Скрипт управления (Linux/macOS)
├── manage.bat                    # Скрипт управления (Windows)
├── README.md                     # Полная документация
├── QUICKSTART.md                 # Быстрый старт
├── AUTOSTART.md                  # Настройка автозапуска
├── PROJECT_STRUCTURE.md          # Этот файл
├── Dockerfile                    # Docker образ
├── docker-compose.yml            # Docker Compose конфигурация
├── aniliberty-updater.service    # Systemd сервис (Linux)
├── com.aniliberty.updater.plist  # LaunchAgent (macOS)
├── .gitignore                    # Git ignore правила
├── auto_update_torrents.log      # Лог-файл (создается автоматически)
└── temp_torrents/                # Временные торрент-файлы (создается автоматически)
```

## Описание файлов

### Основные файлы

**auto_update_torrents.py**
- Основной Python скрипт
- Содержит всю логику работы с API
- Классы: Config, AniLibertyAPI, QBittorrentAPI, TorrentUpdater

**requirements.txt**
- Список Python зависимостей
- Только `requests` библиотека

**config.json**
- Конфигурация приложения
- Создается из config.example.json при установке
- Содержит настройки API и список отслеживаемых релизов
- НЕ должен попадать в git (в .gitignore)

**state.json**
- Сохраняет состояние между запусками
- Хранит hash последних торрентов для каждого релиза
- Создается автоматически при первом запуске
- НЕ должен попадать в git (в .gitignore)

### Документация

**README.md**
- Полная документация проекта
- Описание возможностей
- Инструкции по установке и настройке
- Примеры использования
- Устранение неполадок

**QUICKSTART.md**
- Краткая инструкция для быстрого старта
- 4 простых шага для начала работы

**AUTOSTART.md**
- Инструкции по настройке автозапуска
- Для Linux (systemd), macOS (launchd), Windows (Task Scheduler)
- Примеры для Docker

**PROJECT_STRUCTURE.md**
- Описание структуры проекта
- Назначение каждого файла

### Скрипты управления

**manage.sh** (Linux/macOS)
- Bash скрипт для управления
- Команды: start, stop, restart, status, check, add, logs, install
- Исполняемый файл (chmod +x)

**manage.bat** (Windows)
- Batch скрипт для управления
- Те же команды, что и в manage.sh
- Для Windows командной строки

### Docker

**Dockerfile**
- Описание Docker образа
- Базовый образ: python:3.11-slim
- Устанавливает зависимости и копирует скрипт

**docker-compose.yml**
- Docker Compose конфигурация
- Настройки volumes и network
- Автоматический перезапуск

### Автозапуск

**aniliberty-updater.service**
- Systemd unit файл для Linux
- Требует замены %USER% и %WORKING_DIR%
- Копируется в /etc/systemd/system/

**com.aniliberty.updater.plist**
- LaunchAgent для macOS
- Требует замены %WORKING_DIR%
- Копируется в ~/Library/LaunchAgents/

### Другие файлы

**.gitignore**
- Правила игнорирования для git
- Исключает config.json, state.json, логи, временные файлы

**auto_update_torrents.log**
- Лог-файл приложения
- Создается автоматически при первом запуске
- Содержит все операции и ошибки

**temp_torrents/**
- Директория для временных торрент-файлов
- Создается автоматически
- Файлы удаляются после добавления в qBittorrent

## Файлы, которые НЕ должны попадать в git

- config.json (содержит пароли)
- state.json (локальное состояние)
- *.log (логи)
- temp_torrents/ (временные файлы)
- *.pid (PID файлы)
- __pycache__/ (Python кэш)

Все эти файлы уже добавлены в .gitignore

## Минимальный набор для работы

Для работы скрипта необходимы только:
1. auto_update_torrents.py
2. requirements.txt
3. config.json (создать из config.example.json)

Все остальные файлы - это документация и вспомогательные скрипты.
