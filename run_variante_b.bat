@echo off
title SPL Django - Variante B (Sistema Completo)
cd /d "%~dp0"
set SPL_VARIANT=PRODUCT_B
echo ============================================================
echo  Iniciando Sistema Web Django - VARIANTE B (Sistema Completo)
echo  ENABLE_REPORTS=True ^| ENABLE_NOTIFICATIONS=True
echo  URL: http://127.0.0.1:8002/
echo ============================================================
venv\Scripts\python.exe manage.py runserver 8002
pause
