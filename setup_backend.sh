#!/bin/bash
# Quick setup script for Financial Forecasting MVP Backend

echo "Setting up Financial Forecasting MVP Backend..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # For Mac/Linux
# For Windows: venv\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo "Please edit backend/.env with your database credentials"
fi

# Create PostgreSQL database
echo "Creating PostgreSQL database..."
psql -U postgres -c "CREATE DATABASE financial_forecasting;" 2>/dev/null || echo "Database might already exist"

# Run migrations
echo "Running migrations..."
cd backend
python manage.py makemigrations forecasting
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

echo "Setup complete!"
echo "To start the backend, run:"
echo "cd backend"
echo "python manage.py runserver"

