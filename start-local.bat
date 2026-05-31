@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\start-local-server.ps1" -Port 8080
