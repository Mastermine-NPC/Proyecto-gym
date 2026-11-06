@echo off
chcp 65001 > nul
echo ======================================================================
echo        AURAFIT GYM - EJECUCIÓN DE PRUEBAS AUTOMATIZADAS (CI)
echo ======================================================================
echo.
set USE_SQLITE=True

echo [1/3] Verificando estado del sistema Django (System Check)...
.\.venv\Scripts\python.exe manage.py check
echo.

echo [2/3] Verificando consistencia de migraciones...
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
echo.

echo [3/3] Ejecutando pruebas unitarias, API y Paradigmas...
.\.venv\Scripts\python.exe manage.py test apps paradigmas.pruebas --verbosity 2
echo.
echo ======================================================================
pause

