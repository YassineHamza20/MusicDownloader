@echo off
cd /d "%~dp0"
git commit --allow-empty -m "Daily activity %date% %time%"
git push
pause