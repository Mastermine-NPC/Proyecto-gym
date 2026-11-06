@echo off
chcp 65001 > nul
echo ======================================================================
echo           AURAFIT GYM - INICIAR SERVIDOR PARA PRUEBAS
echo ======================================================================
echo.
echo Seleccione el motor de Base de Datos para la prueba:
echo [1] PostgreSQL (Requiere servicio PostgreSQL activo en puerto 5432)
echo [2] SQLite (Listo para usar de inmediato, sin requerir servidor externo)
echo.
set /p DB_OPCION="Seleccione opción (1 o 2, por defecto 2): "

if "%DB_OPCION%"=="1" (
    echo Configurando conexión con PostgreSQL...
    set USE_SQLITE=False
) else (
    echo Configurando conexión con SQLite (db.sqlite3)...
    set USE_SQLITE=True
)

echo.
echo Aplicando migraciones a la Base de Datos seleccionada...
.\.venv\Scripts\python.exe manage.py migrate

echo.
echo Iniciando servidor Django en http://127.0.0.1:8000 ...
echo Mantenga esta ventana abierta mientras ejecuta Locust.
echo.
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
