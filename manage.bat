@echo off
REM Скрипт для управления AniLiberty Torrent Updater (Windows)

cd /d "%~dp0"

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="check" goto check
if "%1"=="add" goto add
if "%1"=="logs" goto logs
if "%1"=="install" goto install
goto usage

:start
echo Запуск мониторинга...
start /B pythonw auto_update_torrents.py
echo Запущено в фоновом режиме
goto end

:stop
echo Остановка процесса...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq auto_update_torrents*"
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq auto_update_torrents*"
echo Остановлено
goto end

:check
echo Выполнение одной проверки...
python auto_update_torrents.py --once
goto end

:add
if "%2"=="" (
    echo Использование: %0 add ^<release_id^>
    goto end
)
echo Добавление релиза %2 в отслеживание...
python auto_update_torrents.py --add-release %2
goto end

:logs
if exist auto_update_torrents.log (
    type auto_update_torrents.log
) else (
    echo Лог-файл не найден
)
goto end

:install
echo Установка зависимостей...
pip install -r requirements.txt

if not exist config.json (
    echo Создание config.json из примера...
    copy config.example.json config.json
    echo Отредактируйте config.json перед запуском!
)

echo Установка завершена
goto end

:usage
echo Использование: %0 {start^|stop^|check^|add^|logs^|install}
echo.
echo Команды:
echo   start    - Запустить мониторинг в фоне
echo   stop     - Остановить мониторинг
echo   check    - Выполнить одну проверку
echo   add ID   - Добавить релиз в отслеживание
echo   logs     - Показать логи
echo   install  - Установить зависимости
goto end

:end
