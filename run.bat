@echo off
echo 🚀 Iniciando Creador de Historias Visuales...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar si el archivo .env existe
if not exist ".env" (
    echo ⚠️ Archivo .env no encontrado
    echo 💡 Crea un archivo .env con las variables necesarias
    echo 📖 Consulta el README.md para más información
    echo.
)

REM Crear directorio de historias si no existe
if not exist "stories" mkdir stories

REM Ejecutar la aplicación
echo 🌐 Abriendo aplicación en el navegador...
python -m streamlit run main.py --server.headless false --server.port 8501

pause