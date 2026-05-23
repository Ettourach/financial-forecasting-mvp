@echo off
REM Quick setup script for Financial Forecasting MVP Backend (Windows)

echo Setting up Financial Forecasting MVP Backend...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    echo Creating .env file...
    copy backend\.env.example backend\.env
    echo Please edit backend\.env with your database credentials
)

REM Run migrations
echo Running migrations...
cd backend
python manage.py makemigrations forecasting
python manage.py migrate

REM Create superuser
echo Creating superuser...
python manage.py createsuperuser

echo Setup complete!
echo To start the backend, run:
echo cd backend
echo python manage.py runserver
pause

