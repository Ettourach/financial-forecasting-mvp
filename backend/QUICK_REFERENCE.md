# Backend Quick Reference Guide

## Quick Start

### 1. First Time Setup (5 minutes)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Server will be available at: **http://localhost:8000**

### 2. Running Tests

```bash
python manage.py test forecasting.tests
```

Expected output:
```
Ran 3 tests in 0.058s
OK
```

### 3. Creating Superuser

```bash
python manage.py createsuperuser
# Then visit http://localhost:8000/admin/
```

## API Endpoints Quick Reference

### Health Check
```bash
GET http://localhost:8000/api/health/
```

**Response:**
```json
{
  "success": true,
  "message": "Backend is healthy",
  "data": {"status": "ok"}
}
```

### Upload CSV Data
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F "file=@your_data.csv" \
  -F "symbol=AAPL" \
  -F "timeframe=1d"
```

**CSV Format (Required Columns)**
```
timestamp,open,high,low,close,volume
2024-01-01,185.10,187.30,184.20,186.50,54122000
2024-01-02,186.40,188.10,185.00,187.80,49345000
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Dataset uploaded successfully",
  "data": {
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "AAPL",
    "timeframe": "1d",
    "rows_processed": 2,
    "status": "validated"
  }
}
```

### Get Dataset Details
```bash
GET http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/
```

**Response:**
```json
{
  "success": true,
  "message": "Dataset retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "AAPL",
    "timeframe": "1d",
    "rows_count": 2,
    "status": "validated",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-02T00:00:00Z",
    "statistics": {
      "mean_price": 187.15,
      "min_price": 184.20,
      "max_price": 188.10
    }
  }
}
```

### Get Candlestick Data
```bash
GET http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/candlesticks/?limit=100
```

**Response:**
```json
{
  "success": true,
  "message": "Candlesticks retrieved successfully",
  "data": {
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "AAPL",
    "timeframe": "1d",
    "count": 2,
    "candlesticks": [
      {
        "id": "...",
        "timestamp": "2024-01-01T00:00:00Z",
        "open_price": "185.10",
        "high_price": "187.30",
        "low_price": "184.20",
        "close_price": "186.50",
        "volume": "54122000"
      },
      ...
    ]
  }
}
```

### Generate Prediction
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "horizon": 30,
    "model": "default",
    "confidence": 0.95
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Prediction generated successfully",
  "data": {
    "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "AAPL",
    "model": "default",
    "horizon": 30,
    "confidence": 0.95,
    "predictions": [
      {"period": 1, "predicted_close": 187.08},
      {"period": 2, "predicted_close": 187.09},
      ...
    ],
    "status": "completed"
  }
}
```

## Project Structure

```
backend/
├── config/
│   ├── settings.py          ← Django settings
│   ├── urls.py              ← URL routing
│   └── wsgi.py              ← WSGI application
├── core/
│   ├── exceptions.py        ← Custom exceptions
│   ├── response.py          ← Response formatter
│   └── pagination.py        ← Pagination utilities
├── forecasting/
│   ├── models/
│   │   └── candlestick.py   ← Database models
│   ├── serializers/
│   │   └── candlestick.py   ← DRF serializers
│   ├── services/
│   │   ├── csv_parser.py    ← CSV processing
│   │   ├── validation.py    ← Business validation
│   │   └── dataset.py       ← Dataset operations
│   ├── api/
│   │   ├── views.py         ← API endpoints
│   │   ├── validators.py    ← Request validators
│   │   └── urls.py          ← API URLs
│   ├── migrations/          ← Database migrations
│   ├── tests/
│   │   └── test_api.py      ← Unit tests
│   └── admin.py             ← Django admin config
├── manage.py                ← Django CLI
├── requirements.txt         ← Python dependencies
├── .env.example             ← Environment template
├── .env                     ← Environment variables (local)
├── Dockerfile               ← Docker build config
├── README.md                ← Backend documentation
└── ARCHITECTURE.md          ← Architecture details
```

## Database Models

### UploadedDataset
Stores metadata about uploaded CSV files.

**Fields:**
- `id` (UUID): Primary key
- `symbol` (str): Trading symbol (e.g., "AAPL")
- `timeframe` (str): Candlestick interval (e.g., "1d", "1h")
- `rows_count` (int): Number of records
- `status` (str): pending/validated/completed/failed
- `created_at` (datetime): Upload timestamp

### CandlestickData
Individual OHLCV candlestick records.

**Fields:**
- `id` (UUID): Primary key
- `dataset` (FK): Reference to UploadedDataset
- `timestamp` (datetime): Candle timestamp
- `open_price`, `high_price`, `low_price`, `close_price` (Decimal): OHLC prices
- `volume` (Decimal): Trading volume

### PredictionResult
Stores forecasting results.

**Fields:**
- `id` (UUID): Primary key
- `dataset` (FK): Reference to UploadedDataset
- `model_name` (str): Model type used
- `horizon` (int): Number of periods forecasted
- `predictions` (JSON): Array of predicted values
- `status` (str): pending/completed/failed

## Environment Variables

### Required (Development)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Optional (Production)
```env
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=financial_forecasting
DB_USER=postgres
DB_PASSWORD=strong_password
DB_HOST=db.example.com
DB_PORT=5432
ALLOWED_HOSTS=api.example.com,www.example.com
CORS_ALLOWED_ORIGINS=https://app.example.com
```

## Common Tasks

### Run Migrations
```bash
python manage.py makemigrations forecasting
python manage.py migrate
```

### Check Code Style
```bash
# Install flake8
pip install flake8

# Check formatting
flake8 forecasting/
```

### Database Backup (SQLite)
```bash
cp db.sqlite3 db.backup.sqlite3
```

### Database Backup (PostgreSQL)
```bash
pg_dump -U postgres financial_forecasting > backup.sql
```

### Restart with Fresh Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Debugging

### Enable Debug Mode
```env
DEBUG=True
```

### Check Logs
- Django errors: `logs/django.log`
- Application logs: Console output

### Test Database Connection
```bash
python manage.py shell
>>> from django.db import connection
>>> print(connection)
```

### Inspect Models
```bash
python manage.py inspect_models
python manage.py sqlmigrate forecasting 0001
```

## Performance Tips

1. **Use pagination**: Always use `?page=1&page_size=100` for large datasets
2. **Filter early**: Use query parameters to reduce data transfer
3. **Bulk operations**: Use `bulk_create()` for multiple inserts
4. **Index often-queried columns**: Already done in models
5. **Cache results**: Use Django's cache framework for repeated queries

## Troubleshooting

### `django.core.exceptions.DisallowedHost`
**Solution**: Add your hostname to `ALLOWED_HOSTS` in `.env`

### `ModuleNotFoundError`
**Solution**: Reinstall dependencies: `pip install -r requirements.txt`

### Database locked (SQLite)
**Solution**: WAL mode is enabled by default. For single-process, ensure only one process accesses the database.

### Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000    # Windows
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## Support

For issues or questions:
1. Check the [README.md](README.md) for overview
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
3. Check test cases in `forecasting/tests/`
4. Review inline code comments

---

**Last Updated**: May 11, 2026
**Backend Version**: 1.0.0

