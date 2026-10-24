@echo off
chcp 65001 >nul
title Orakul Studio - Archivist Updater

echo =======================================================
echo         Orakul Archivist - Auto Updater
echo =======================================================
echo.

python updater.py

echo.
pause