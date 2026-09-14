@echo off
rem What Task Scheduler runs. The API key comes from the permanent user variable set with setx.
cd /d "%~dp0"
.venv\Scripts\python.exe main.py demo "Organise any new files in this folder the same way as before." --auto-approve
