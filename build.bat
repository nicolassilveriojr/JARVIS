@echo off
echo.
echo ========================================
echo   JARVIS - Compilando para EXE
echo ========================================
echo.

if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del *.spec

echo [1/2] Compilando...
pyinstaller --onefile --windowed --name=JARVIS ^
    --add-data ".env;." ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --add-data "utils;utils" ^
    --collect-all customtkinter ^
    main.py

echo.
if exist "dist\JARVIS.exe" (
    echo ========================================
    echo  SUCESSO! Arquivo em: dist\JARVIS.exe
    echo ========================================
) else (
    echo  ERRO ao compilar!
)
echo.
pause
