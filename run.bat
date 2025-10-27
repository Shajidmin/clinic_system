@echo off
setlocal

REM Change to script directory (manage.py location)
cd /d "%~dp0"

REM Activate virtual environment (expects venv folder next to manage.py)
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
) else (
    echo Virtual environment not found at "%~dp0venv%". Create one with:
    echo   python -m venv venv
    pause
    exit /b 1
)

echo.
echo Upgrading pip and installing minimal requirements (safe to skip if already installed)...
pip install --upgrade pip
pip install django django-multiselectfield django-bootstrap5

echo.
echo Making migrations...
python "%~dp0manage.py" makemigrations

echo Applying migrations...
python "%~dp0manage.py" migrate

echo.
REM If you set DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD env vars, create superuser non-interactively
if defined DJANGO_SUPERUSER_USERNAME (
    if not defined DJANGO_SUPERUSER_EMAIL set DJANGO_SUPERUSER_EMAIL=admin@example.com
    echo Creating superuser %DJANGO_SUPERUSER_USERNAME% ...
    python "%~dp0manage.py" init_system --username "%DJANGO_SUPERUSER_USERNAME%" --email "%DJANGO_SUPERUSER_EMAIL%" --password "%DJANGO_SUPERUSER_PASSWORD%"
) else (
    echo To auto-create a superuser, set environment variables:
    echo   set DJANGO_SUPERUSER_USERNAME=admin
    echo   set DJANGO_SUPERUSER_EMAIL=admin@example.com
    echo   set DJANGO_SUPERUSER_PASSWORD=YourPassHere
)

echo.
echo Starting development server on 0.0.0.0:8000
python "%~dp0manage.py" runserver 0.0.0.0:8000

endlocal
