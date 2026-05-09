# Руководство по использованию

## Новые возможности

### 🔍 Поиск релизов по названию

Теперь не нужно искать ID релиза вручную на сайте!

```bash
# Поиск релизов
./manage.sh search "Хайбара"
./manage.sh search "Доктор Стоун"
```

Результат:
```
Найдено релизов: 10

1. ID: 10159
   Название: Вторая юность Хайбары
   English: Haibara-kun no Tsuyokute Seishun New Game
   Год: 2026 | Тип: ТВ | Эпизодов: 12

2. ID: 10162
   Название: Доктор Стоун: Научное будущее. Часть 3
   English: Dr. Stone: Science Future Part 3
   Год: 2026 | Тип: ТВ | Эпизодов: 12
...
```

### 📁 Указание пути сохранения

Каждый релиз может сохраняться в свою папку!

#### Способ 1: Добавление по ID с путем

```bash
./manage.sh add 10162 /downloads/anime/dr-stone
```

#### Способ 2: Интерактивное добавление по названию

```bash
./manage.sh add-by-name "Доктор Стоун"
```

Скрипт покажет найденные релизы и предложит выбрать:
```
Найдено релизов: 3

1. Доктор Стоун: Научное будущее. Часть 3
   (Dr. Stone: Science Future Part 3)
   ID: 10162 | Год: 2026

2. Доктор Стоун 3
   (Dr. Stone: New World)
   ID: 8234 | Год: 2023

3. Доктор Стоун 2
   (Dr. Stone: Stone Wars)
   ID: 6543 | Год: 2021

Выберите номер релиза (0 для отмены): 1
Путь сохранения для 'Доктор Стоун: Научное будущее. Часть 3' (Enter для пути по умолчанию): /downloads/anime/dr-stone

✓ Релиз 'Доктор Стоун: Научное будущее. Часть 3' (ID: 10162) добавлен в отслеживание
  Путь сохранения: /downloads/anime/dr-stone
```

#### Способ 3: Через Python напрямую

```bash
python3 auto_update_torrents.py --add-release 10162 --save-path "/downloads/anime/dr-stone"
python3 auto_update_torrents.py --add-by-name "Хайбара" --save-path "/downloads/anime/haibara"
```

## Структура конфигурации

### config.json (новый формат)

```json
{
    "aniliberty": {
        "api_url": "https://aniliberty.top/api/v1",
        "check_interval": 300
    },
    "qbittorrent": {
        "url": "http://localhost:8080",
        "username": "admin",
        "password": "your_password",
        "download_path": "/downloads/anime"
    },
    "tracked_releases": {
        "10159": {
            "name": "Вторая юность Хайбары",
            "save_path": "/downloads/anime/haibara"
        },
        "10162": {
            "name": "Доктор Стоун: Научное будущее. Часть 3",
            "save_path": "/downloads/anime/dr-stone"
        },
        "10176": {
            "name": "Девушка на час 5",
            "save_path": ""
        }
    }
}
```

### Параметры:

**qbittorrent.download_path** - глобальный путь по умолчанию для всех релизов

**tracked_releases** - словарь релизов:
- Ключ: ID релиза (строка)
- Значение: объект с полями:
  - `name` - название релиза (автоматически)
  - `save_path` - путь сохранения для этого релиза
    - Если пустая строка `""` - используется `qbittorrent.download_path`
    - Если не указан - используется путь по умолчанию qBittorrent

## Приоритет путей сохранения

1. **Путь релиза** (`tracked_releases[ID].save_path`) - если указан
2. **Глобальный путь** (`qbittorrent.download_path`) - если путь релиза пустой
3. **Путь по умолчанию qBittorrent** - если оба не указаны

## Примеры использования

### Пример 1: Организация по папкам

```bash
# Добавляем релизы в разные папки
./manage.sh add 10159 /downloads/anime/ongoing/haibara
./manage.sh add 10162 /downloads/anime/ongoing/dr-stone
./manage.sh add 10176 /downloads/anime/ongoing/kanojo
```

### Пример 2: Использование глобального пути

Установите `download_path` в config.json:
```json
"qbittorrent": {
    "download_path": "/downloads/anime/ongoing"
}
```

Затем добавляйте релизы без указания пути:
```bash
./manage.sh add 10159
./manage.sh add 10162
```

Все будут сохраняться в `/downloads/anime/ongoing`

### Пример 3: Смешанный подход

```json
"qbittorrent": {
    "download_path": "/downloads/anime"
},
"tracked_releases": {
    "10159": {
        "name": "Вторая юность Хайбары",
        "save_path": "/downloads/anime/favorites/haibara"
    },
    "10162": {
        "name": "Доктор Стоун",
        "save_path": ""
    }
}
```

- Релиз 10159 → `/downloads/anime/favorites/haibara`
- Релиз 10162 → `/downloads/anime` (глобальный путь)

## Все команды manage.sh

```bash
./manage.sh start                          # Запустить мониторинг
./manage.sh stop                           # Остановить мониторинг
./manage.sh restart                        # Перезапустить
./manage.sh status                         # Проверить статус
./manage.sh check                          # Одна проверка
./manage.sh add 10159                      # Добавить по ID
./manage.sh add 10159 /path/to/save        # Добавить с путем
./manage.sh search "название"              # Поиск релизов
./manage.sh add-by-name "название"         # Интерактивное добавление
./manage.sh add-by-name "название" /path   # С путем
./manage.sh logs                           # Показать логи
./manage.sh install                        # Установить зависимости
```

## Проверка работы

После добавления релиза выполните проверку:

```bash
./manage.sh check
```

Проверьте логи:
```bash
tail -20 auto_update_torrents.log
```

Проверьте qBittorrent - торрент должен быть добавлен с правильным путем сохранения.

## Миграция со старой версии

Если у вас старый формат config.json:

**Старый формат:**
```json
"tracked_releases": [4754, 5123]
```

**Новый формат:**
```json
"tracked_releases": {
    "4754": {
        "name": "Название релиза",
        "save_path": ""
    },
    "5123": {
        "name": "Другой релиз",
        "save_path": "/custom/path"
    }
}
```

Скрипт автоматически создаст новый формат при добавлении релизов через команды.

## Советы

1. **Используйте абсолютные пути** - `/downloads/anime` вместо `~/downloads`
2. **Создайте папки заранее** - qBittorrent должен иметь права на запись
3. **Проверяйте пути** - опечатка в пути может привести к ошибке
4. **Используйте поиск** - быстрее чем искать ID на сайте
5. **Организуйте структуру** - например `/downloads/anime/ongoing`, `/downloads/anime/completed`
