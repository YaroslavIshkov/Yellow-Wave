@echo off
echo ============================================
echo   Building Yellow Wave to .exe (onedir)
echo ============================================
echo.

REM Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [X] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/2] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist YellowWave.spec del /q YellowWave.spec

echo [2/2] Building...
python -m PyInstaller ^
    --onedir ^
    --noconsole ^
    --name YellowWave ^
    --icon "icon.ico" ^
    --hidden-import mutagen ^
    --hidden-import pygame ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    main.py

if errorlevel 1 (
    echo.
    echo [X] Build failed
    pause
    exit /b 1
)

echo [3/3] Copying resources...
xcopy /E /I /Y "icons" "dist\YellowWave\icons" >nul
xcopy /E /I /Y "fonts" "dist\YellowWave\fonts" >nul
xcopy /E /I /Y "Playlists" "dist\YellowWave\Playlists" >nul
if exist "icon.ico" copy /Y "icon.ico" "dist\YellowWave" >nul
if exist "close.ico" copy /Y "close.ico" "dist\YellowWave" >nul

echo.
echo ============================================
echo   DONE!
echo   .exe: dist\YellowWave\YellowWave.exe
echo ============================================
echo.
echo [Important] Copy these into dist\YellowWave\:
echo   - Playlists\
echo   - config\  (or it will be created)
echo.
pause