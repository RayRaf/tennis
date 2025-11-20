@echo off
REM Запуск Django сервера для разработки с WebSocket поддержкой

echo ====================================
echo Запуск Tennis приложения (dev mode)
echo ====================================
echo.

cd /d "%~dp0tennis"

echo Используем settings_dev.py для локальной разработки...
set DJANGO_SETTINGS_MODULE=tennis.settings_dev

echo.
echo Запуск Daphne сервера на http://localhost:8000
echo Для остановки нажмите Ctrl+C
echo.

python manage.py runserver
