@echo off
title Usman Automize PC Tool v2 - Install
cd /d "%~dp0"
echo ==================================================
echo    USMAN AUTOMIZE - PC TOOL v2 - INSTALL (pehli dafa)
echo ==================================================
echo.
set PY=
py -3.12 -c "import sys" >nul 2>nul && set PY=py -3.12
if not defined PY (py -3.11 -c "import sys" >nul 2>nul && set PY=py -3.11)
if not defined PY (python -c "import sys" >nul 2>nul && set PY=python)
if not defined PY (py -3 -c "import sys" >nul 2>nul && set PY=py -3)
if not defined PY (
  echo Python nahi mila!
  echo 1. https://www.python.org/downloads/ se Python 3.12 download karein.
  echo 2. Install karte waqt "Add python.exe to PATH" par TICK zaroor lagayein.
  echo 3. Phir yeh INSTALL.bat dobara chalayein.
  start https://www.python.org/downloads/
  pause
  exit /b
)
echo Python mil gaya:
%PY% --version
echo.
echo [1/2] Zaroori packages install ho rahe hain...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
  echo Packages install nahi hue. Python 3.12 hona chahiye, phir dobara chalao.
  pause
  exit /b
)
echo.
echo [2/2] Video engine (ffmpeg)...
%PY% setup_ffmpeg.py
echo.
echo ==================================================
echo   INSTALL MUKAMMAL! Ab START.bat chalayein.
echo ==================================================
pause
