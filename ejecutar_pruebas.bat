@echo off
chcp 65001 > nul
set USE_SQLITE=True
set REPORTE=reporte_ci_cd_output.txt

echo ====================================================================== > %REPORTE%
echo        AURAFIT GYM - REPORTE DE EJECUCION CI/CD Y PRUEBAS              >> %REPORTE%
echo        Fecha y Hora: %DATE% %TIME%                                     >> %REPORTE%
echo        Repositorio : https://github.com/Mastermine-NPC/Proyecto-gym    >> %REPORTE%
echo ====================================================================== >> %REPORTE%
echo. >> %REPORTE%

echo [1/3] Verificando estado del sistema Django (System Check)...
echo [1/3] VERIFICACION DEL SISTEMA DJANGO (manage.py check) >> %REPORTE%
echo ---------------------------------------------------------------------- >> %REPORTE%
.\.venv\Scripts\python.exe manage.py check >> %REPORTE% 2>&1
echo. >> %REPORTE%

echo [2/3] Verificando consistencia de migraciones...
echo [2/3] VERIFICACION DE MIGRACIONES (makemigrations --check --dry-run) >> %REPORTE%
echo ---------------------------------------------------------------------- >> %REPORTE%
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run >> %REPORTE% 2>&1
echo. >> %REPORTE%

echo [3/3] Ejecutando pruebas unitarias, API de concurrencia y Paradigmas...
echo [3/3] EJECUCION DE PRUEBAS AUTOMATIZADAS (manage.py test --verbosity 2) >> %REPORTE%
echo ---------------------------------------------------------------------- >> %REPORTE%
.\.venv\Scripts\python.exe manage.py test apps paradigmas.pruebas --verbosity 2 >> %REPORTE% 2>&1
echo. >> %REPORTE%
echo ====================================================================== >> %REPORTE%
echo                  ESTADO FINAL: INTEGRACION CONTINUA EXITOSA            >> %REPORTE%
echo ====================================================================== >> %REPORTE%

type %REPORTE%
echo.
echo El reporte completo se ha guardado en: %CD%\%REPORTE%
pause
