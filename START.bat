@echo off
title Usman Automize PC Tool v2 - is window ko KHULA rakhein
cd /d "%~dp0"
set PY=
py -3.12 -c "import sys" >nul 2>nul && set PY=py -3.12
if not defined PY (py -3.11 -c "import sys" >nul 2>nul && set PY=py -3.11)
if not defined PY (python -c "import sys" >nul 2>nul && set PY=python)
if not defined PY (py -3 -c "import sys" >nul 2>nul && set PY=py -3)
if not defined PY (
  echo Python nahi mila. Pehle INSTALL.bat chalayein.
  pause
  exit /b
)
echo Usman Automize PC Tool v2 chal raha hai...
echo Browser mein khud khul jayega: http://localhost:4100
echo Band karne ke liye is window mein Ctrl+C dabao.
%PY% server.py
if errorlevel 1 (
  echo.
  echo Koi masla aaya. Upar wala message dekhein, ya INSTALL.bat dobara chalayein.
  pause
)
