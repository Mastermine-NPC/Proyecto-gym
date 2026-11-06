@echo off
chcp 65001 > nul
echo ======================================================================
echo           AURAFIT GYM - PRUEBA DE CONCURRENCIA CON LOCUST
echo ======================================================================
echo.
echo Seleccione el modo de ejecución:
echo [1] Iniciar Locust en modo Interfaz Web (Panel Gráfico en http://localhost:8089)
echo [2] Ejecutar prueba directa de 1,000 usuarios concurrentes (Modo Headless)
echo [3] Salir
echo.
set /p OPCION="Ingrese una opción (1-3): "

if "%OPCION%"=="1" (
    echo.
    echo Iniciando Locust Web en http://localhost:8089...
    echo Abra su navegador en: http://localhost:8089
    echo Host predeterminado: http://127.0.0.1:8000
    echo Número de usuarios: 1000
    echo Spawn rate: 50
    echo.
    .\.venv\Scripts\locust.exe -f locustfile.py --host http://127.0.0.1:8000
) else if "%OPCION%"=="2" (
    echo.
    echo ======================================================================
    echo  LANZANDO PRUEBA DE CARGA: 1,000 USUARIOS CONCURRENTES
    echo  Inscripción masiva de clientes directamente en la Base de Datos...
    echo ======================================================================
    echo.
    .\.venv\Scripts\locust.exe -f locustfile.py --host http://127.0.0.1:8000 --headless -u 1000 -r 50 --run-time 1m --html reporte_concurrencia_1000.html
    echo.
    echo ======================================================================
    echo  Prueba completada. Reporte HTML generado: reporte_concurrencia_1000.html
    echo ======================================================================
    pause
) else (
    echo Saliendo...
)
