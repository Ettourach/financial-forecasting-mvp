# Financial Forecasting MVP - Backend

Production-ready Django REST API backend for financial forecasting MVP application.

## Overview

This backend provides a robust API for:
- Uploading and validating candlestick CSV data
- Storing market data in PostgreSQL
- Generating price predictions
- Querying historical and predicted data

## Tech Stack

- **Django 6.0+** - Web framework
- **Django REST Framework 3.14+** - API development
- **PostgreSQL** - Database
- **Pandas** - Data processing
- **Gunicorn** - Production server
- **Python 3.12** - Runtime

## Project Structure

```
backend/
├── config/              # Django settings and WSGI
│   ├── settings.py      # Main configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI application
├── core/                # Shared utilities
│   ├── exceptions.py    # Custom exceptions
│   ├── response.py      # Response formatter
│   └── pagination.py    # Pagination utilities
├── forecasting/         # Main app
│   ├── models/          # Database models
│   ├── serializers/     # DRF serializers
│   ├── services/        # Business logic
│   ├── api/             # Views and URLs
│   ├── admin.py         # Django admin
│   └── migrations/      # Database migrations
├── manage.py            # Django CLI
└── .env.example         # Environment template
```

## Installation

### 1. Clone and navigate to backend

```bash
cd backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r ../requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Create PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE financial_forecasting;"
```

### 6. Run migrations

```bash
python manage.py makemigrations forecasting
python manage.py migrate
```

### 7. Create superuser (for admin)

```bash
python manage.py createsuperuser
```

### 8. Run development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Upload CSV Data

**POST** `/api/upload/`

Upload candlestick CSV file with columns: timestamp, open, high, low, close, volume

```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F "file=@data.csv" \
  -F "symbol=AAPL" \
  -F "timeframe=1d"
```

**Response:**
```json
{
  "success": true,
  "message": "Dataset uploaded successfully",
  "data": {
    "dataset_id": "uuid",
    "symbol": "AAPL",
    "timeframe": "1d",
    "rows_processed": 2450,
    "status": "validated"
  }
}
```

### Get Dataset Details

**GET** `/api/datasets/{dataset_id}/`

Retrieve details about an uploaded dataset.

```bash
curl http://localhost:8000/api/datasets/uuid/
```

### Get Dataset Candlesticks

**GET** `/api/datasets/{dataset_id}/candlesticks/`

Retrieve candlestick records for a dataset (supports pagination).

```bash
curl http://localhost:8000/api/datasets/uuid/candlesticks/?limit=1000
```

### Generate Prediction

**POST** `/api/predict/`

Generate a price prediction for a dataset.

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "uuid",
    "horizon": 30,
    "model": "default",
    "confidence": 0.95
  }'
```

### Health Check

**GET** `/api/health/`

Check API status.

```bash
curl http://localhost:8000/api/health/
```

## Architecture

### Models Layer

- **UploadedDataset** - Metadata for CSV uploads
- **CandlestickData** - Individual OHLCV records
- **PredictionResult** - Forecast results and metadata

### Services Layer

- **CSVParserService** - CSV parsing and validation
- **ValidationService** - Business rule validation
- **DatasetService** - Dataset CRUD and operations

### API Layer

- **UploadCSVView** - CSV upload endpoint
- **DatasetDetailView** - Dataset details
- **DatasetCandlesticksView** - Query candlestick data
- **PredictionView** - Generate predictions
- **HealthCheckView** - Health check

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Configure in `.env`:

```env
JWT_SECRET=your-secret-key
```

For public endpoints, set `permission_classes = [AllowAny]` in views.

## Database

PostgreSQL configuration in `.env`:

```env
DB_NAME=financial_forecasting
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

## Admin Panel

Access Django admin at `http://localhost:8000/admin/`

- View uploaded datasets
- Inspect candlestick data
- Monitor prediction results

## Testing

Run tests:

```bash
python manage.py test forecasting
```

Run specific test:

```bash
python manage.py test forecasting.tests.test_api.CSVUploadTestCase
```

## Deployment

### Production Settings

Set in `.env`:

```env
DEBUG=False
SECRET_KEY=generate-a-new-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Run with Gunicorn

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync
```

### Docker

Build image:

```bash
docker build -t financial-forecasting-backend .
```

Run container:

```bash
docker run -d \
  -e DB_HOST=postgres \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -p 8000:8000 \
  financial-forecasting-backend
```

## Error Handling

All errors return standardized JSON responses:

```json
{
  "success": false,
  "message": "Error description",
  "code": "error_code",
  "errors": {
    "field": ["error message"]
  }
}
```

## Logging

Logs are stored in `backend/logs/django.log`

Configure in `config/settings.py`:

```python
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
}
```

## Contributing

1. Follow PEP8 style guide
2. Add type hints to functions
3. Write tests for new features
4. Update documentation
5. Create pull request

## Future Features

- Kronos model integration
- Real-time forecasting
- User authentication
- Advanced analytics
- Model versioning
- Performance monitoring

---

For questions or issues, see main [README.md](../README.md)

