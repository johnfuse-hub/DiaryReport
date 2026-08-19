@echo off
chcp 65001 >nul
echo ============================================================
echo   🚀 เริ่มต้น Localhost Web Server (Port 8000)
echo ============================================================
echo กำลังเปิดเว็บที่ http://localhost:8000 ...
start http://localhost:8000
python -m http.server 8000
pause
