@echo off
title SPL Django - Variante A (Sistema Basico)
cd /d "%~dp0"
set SPL_VARIANT=PRODUCT_A
echo ============================================================
echo  Iniciando Sistema Web Django - VARIANTE A (Sistema Basico)
echo  ENABLE_REPORTS=False ^| ENABLE_NOTIFICATIONS=False
echo  URL: http://127.0.0.1:8001/
echo ============================================================
venv\Scripts\python.exe manage.py runserver 8001
pause
