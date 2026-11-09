@echo off
title TaskFlow Server
cd /d "%~dp0"
echo Starting TaskFlow Kanban Server...
echo Open your browser at http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server.
echo.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause

