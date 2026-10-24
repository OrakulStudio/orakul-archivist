@echo off
chcp 65001 >nul
title Orakul Studio - System Watchdog Archivist TUI

cd /d "%~dp0"

:: Проверка наличия виртуального окружения
if exist ".venv_archivist\Scripts\activate.bat" goto RUN

echo [!] Настройка изолированного окружения Archivist...
python -m venv .venv_archivist
if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать venv. Проверьте, добавлен ли Python в PATH.
    pause
    exit /b 1
)

call .venv_archivist\Scripts\activate.bat
echo [+] Установка необходимых библиотек (rich)...
python -m pip install --upgrade pip --quiet

if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
) else (
    pip install rich --quiet
)

echo [+] Окружение успешно настроено!
echo.

:RUN
call .venv_archivist\Scripts\activate.bat

:: Запуск TUI-версии утилиты
if exist "orakull_archivist_tui.py" (
    python orakull_archivist_tui.py
) else (
    python orakull_archivist.py
)

exit /b 0