@echo off
setlocal enabledelayedexpansion

:: ===================================================
::   J.A.R.V.I.S - Stark Industries
::   Protocolo de Compilacao Mark III (v3.3)
:: ===================================================

echo [0/3] Limpando processos e builds antigos...
taskkill /f /im JARVIS.exe 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

:: Detecta o Python
set "PYTHON_EXE=py -3"
!PYTHON_EXE! --version >nul 2>&1
if %errorlevel% neq 0 (
    set "PYTHON_EXE=python"
)

echo [1/3] Garantindo PyInstaller e Dependencias...
!PYTHON_EXE! -m pip install --upgrade pip
!PYTHON_EXE! -m pip install pyinstaller cryptography fastapi uvicorn requests --user

echo.
echo [2/3] Compilando JARVIS v3.3 (Supreme Intelligence)...
echo Isso pode levar alguns minutos devido a complexidade neural...
echo.

!PYTHON_EXE! -m PyInstaller --noconfirm --onefile --windowed ^
--name "JARVIS" ^
--add-data "core;core" ^
--add-data "ui;ui" ^
--add-data "utils;utils" ^
--add-data ".env;." ^
--hidden-import=fastapi --hidden-import=uvicorn --hidden-import=cryptography --hidden-import=requests ^
--hidden-import=psutil --hidden-import=pyautogui --hidden-import=cv2 ^
--icon "NONE" ^
main.py

echo.
echo [3/3] Finalizando...
if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo   SUCESSO! O JARVIS v3.3 esta em:
    echo   %~dp0dist\JARVIS.exe
    echo ===================================================
) else (
    echo.
    echo [ERRO] Falha na compilacao do sistema.
)

pause
