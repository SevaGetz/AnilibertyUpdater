# Быстрый старт

## 1. Установка

```bash
# Установить зависимости
./manage.sh install

# Или вручную
pip install -r requirements.txt
cp config.example.json config.json
```

## 2. Настройка

Отредактируйте `config.json`:

```json
{
    "qbittorrent": {
        "url": "http://localhost:8080",
        "username": "admin",
        "password": "ваш_пароль"
    },
    "tracked_releases": []
}
```

## 3. Добавление релизов

```bash
# Добавить релиз по ID
./manage.sh add 4754

# Или вручную отредактировать config.json
```

## 4. Запуск

```bash
# Одна проверка (тест)
./manage.sh check

# Запуск в фоне
./manage.sh start

# Проверить статус
./manage.sh status

# Посмотреть логи
./manage.sh logs
```

## Windows

Используйте `manage.bat` вместо `manage.sh`:

```cmd
manage.bat install
manage.bat add 4754
manage.bat start
```

## Как найти ID релиза

1. Откройте страницу релиза на AniLiberty
2. Посмотрите URL: `https://aniliberty.top/release/4754`
3. ID = `4754`

## Проверка работы

После запуска проверьте лог-файл:

```bash
tail -f auto_update_torrents.log
```

Вы должны увидеть:
- Успешную авторизацию в qBittorrent
- Проверку каждого релиза
- Сообщения об обновлениях (если есть)
