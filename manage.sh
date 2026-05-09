#!/bin/bash
# Скрипт для управления AniLiberty Torrent Updater

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    start)
        echo "Запуск мониторинга..."
        nohup python3 auto_update_torrents.py > output.log 2>&1 &
        echo $! > updater.pid
        echo "Запущено с PID: $(cat updater.pid)"
        ;;

    stop)
        if [ -f updater.pid ]; then
            PID=$(cat updater.pid)
            echo "Остановка процесса $PID..."
            kill $PID 2>/dev/null
            rm updater.pid
            echo "Остановлено"
        else
            echo "PID файл не найден. Процесс не запущен?"
        fi
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        if [ -f updater.pid ]; then
            PID=$(cat updater.pid)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Работает (PID: $PID)"
            else
                echo "Не работает (устаревший PID файл)"
                rm updater.pid
            fi
        else
            echo "Не работает"
        fi
        ;;

    check)
        echo "Выполнение одной проверки..."
        python3 auto_update_torrents.py --once
        ;;

    add)
        if [ -z "$2" ]; then
            echo "Использование: $0 add <release_id> [save_path]"
            exit 1
        fi
        echo "Добавление релиза $2 в отслеживание..."
        if [ -n "$3" ]; then
            python3 auto_update_torrents.py --add-release "$2" --save-path "$3"
        else
            python3 auto_update_torrents.py --add-release "$2"
        fi
        ;;

    search)
        if [ -z "$2" ]; then
            echo "Использование: $0 search <название>"
            exit 1
        fi
        echo "Поиск релизов..."
        python3 auto_update_torrents.py --search "$2"
        ;;

    add-by-name)
        if [ -z "$2" ]; then
            echo "Использование: $0 add-by-name <название> [save_path]"
            exit 1
        fi
        if [ -n "$3" ]; then
            python3 auto_update_torrents.py --add-by-name "$2" --save-path "$3"
        else
            python3 auto_update_torrents.py --add-by-name "$2"
        fi
        ;;

    logs)
        if [ -f auto_update_torrents.log ]; then
            tail -f auto_update_torrents.log
        else
            echo "Лог-файл не найден"
        fi
        ;;

    install)
        echo "Установка зависимостей..."
        pip3 install -r requirements.txt

        if [ ! -f config.json ]; then
            echo "Создание config.json из примера..."
            cp config.example.json config.json
            echo "Отредактируйте config.json перед запуском!"
        fi

        echo "Установка завершена"
        ;;

    *)
        echo "Использование: $0 {start|stop|restart|status|check|add|search|add-by-name|logs|install}"
        echo ""
        echo "Команды:"
        echo "  start              - Запустить мониторинг в фоне"
        echo "  stop               - Остановить мониторинг"
        echo "  restart            - Перезапустить мониторинг"
        echo "  status             - Проверить статус"
        echo "  check              - Выполнить одну проверку"
        echo "  add ID [PATH]      - Добавить релиз по ID с опциональным путем"
        echo "  search NAME        - Найти релиз по названию"
        echo "  add-by-name NAME [PATH] - Добавить релиз по названию (интерактивно)"
        echo "  logs               - Показать логи в реальном времени"
        echo "  install            - Установить зависимости"
        echo ""
        echo "Примеры:"
        echo "  $0 search \"Хайбара\""
        echo "  $0 add 10159 /downloads/anime"
        echo "  $0 add-by-name \"Хайбара\" /downloads/anime"
        exit 1
        ;;
esac
