# Backend Architecture

Production-ready Django REST backend for Financial Forecasting MVP.

## Design Principles

- **Separation of Concerns**: Clear division between API layer, business logic, and data access
- **Service-Oriented**: Business logic encapsulated in reusable service classes
- **Stateless**: REST API follows stateless design principles
- **Scalability**: Database schema designed for production workloads
- **Error Handling**: Standardized exception hierarchy and error responses
- **Type Safety**: Type hints throughout the codebase

## Architectural Layers

### 1. API Layer (`forecasting/api/`)

**Purpose**: HTTP request/response handling and request validation

**Components**:
- `views.py`: Django REST Framework APIView classes
- `validators.py`: Request payload validators
- `urls.py`: URL routing configuration

**Key Classes**:
- `UploadCSVView`: POST /api/upload/ - Handle file uploads
- `DatasetDetailView`: GET /api/datasets/{id}/ - Retrieve dataset details
- `DatasetCandlesticksView`: GET /api/datasets/{id}/candlesticks/ - Query OHLCV data
- `PredictionView`: POST /api/predict/ - Generate forecasts
- `HealthCheckView`: GET /api/health/ - Service status

**Characteristics**:
- Stateless request-response handling
- Input validation via serializers
- Delegates business logic to services
- Returns standardized JSON responses

### 2. Serialization Layer (`forecasting/serializers/`)

**Purpose**: Request/response data validation and transformation

**Components**:
- `candlestick.py`: DRF serializers for all models

**Key Serializers**:
- `CSVUploadSerializer`: Validates file uploads
- `UploadedDatasetSerializer`: Dataset metadata serialization
- `CandlestickDataSerializer`: Individual OHLCV record serialization
- `PredictionRequestSerializer`: Forecast request validation
- `PredictionResultSerializer`: Forecast result serialization

**Characteristics**:
- Enforces data validation rules
- Handles type conversions
- Provides nested serialization
- Read/write field separation

### 3. Service Layer (`forecasting/services/`)

**Purpose**: Business logic encapsulation and reusable operations

**Components**:

#### `csv_parser.py` - CSV Processing Service
```
parse_csv() → DataFrame
validate_columns() → bool
validate_rows() → None
transform_data() → List[Dict]
process_csv_file() → (DataFrame, List[Dict])
```

Responsibilities:
- Parse CSV files into structured data
- Validate required columns
- Enforce data type constraints
- Handle malformed input gracefully
- Transform data for database insertion

#### `validation.py` - Business Rule Validation Service
```
validate_candlestick() → None
validate_symbol() → bool
validate_timeframe() → bool
validate_horizon() → bool
validate_candlesticks_ordered() → None
validate_no_duplicates() → None
```

Responsibilities:
- Implement business rule validation
- Enforce data constraints
- Check data relationships
- Validate parameter ranges

#### `dataset.py` - Dataset Operations Service
```
create_dataset() → UploadedDataset
store_candlesticks() → (int, List[str])
finalize_dataset() → None
get_dataset_candlesticks() → List[Dict]
get_dataset_statistics() → Dict
delete_dataset_cascade() → None
```

Responsibilities:
- Dataset CRUD operations
- Candlestick persistence
- Database transaction management
- Statistical calculations
- Cascade deletion

**Characteristics**:
- Stateless, reusable methods
- Database transaction handling
- Error propagation via exceptions
- No HTTP knowledge (pure business logic)

### 4. Model Layer (`forecasting/models/`)

**Purpose**: Database schema and ORM definitions

**Models**:

#### `UploadedDataset`
```
Fields:
  - id: UUID (primary key)
  - symbol: CharField (max 20)
  - timeframe: CharField (max 10)
  - source: CharField (max 100)
  - filename: CharField (max 255)
  - rows_count: PositiveIntegerField
  - date_from: DateTimeField (nullable)
  - date_to: DateTimeField (nullable)
  - status: CharField (choices: pending, validated, processing, completed, failed)
  - validation_errors: JSONField
  - created_at: DateTimeField (auto_now_add)
  - updated_at: DateTimeField (auto_now)

Indexes:
  - (symbol, -created_at)
  - (status)

Methods:
  - mark_validated()
  - mark_failed(errors)
```

#### `CandlestickData`
```
Fields:
  - id: UUID (primary key)
  - dataset: ForeignKey → UploadedDataset
  - timestamp: DateTimeField (indexed)
  - open_price: DecimalField (15,8)
  - high_price: DecimalField (15,8)
  - low_price: DecimalField (15,8)
  - close_price: DecimalField (15,8)
  - volume: DecimalField (20,8)
  - high_low_diff: DecimalField (computed)
  - close_open_diff: DecimalField (computed)
  - created_at: DateTimeField (auto_now_add)

Indexes:
  - (dataset, timestamp)
  - (timestamp)

Unique Together:
  - (dataset, timestamp)

Properties:
  - Automatic computed field calculation
  - Validates price hierarchy (high >= low)
```

#### `PredictionResult`
```
Fields:
  - id: UUID (primary key)
  - dataset: ForeignKey → UploadedDataset
  - model_name: CharField (max 100)
  - horizon: PositiveIntegerField
  - confidence_level: FloatField
  - predictions: JSONField (array)
  - statistics: JSONField (metrics)
  - status: CharField (choices: pending, processing, completed, failed)
  - error_message: TextField
  - created_at: DateTimeField (auto_now_add)
  - updated_at: DateTimeField (auto_now)
  - completed_at: DateTimeField (nullable)

Indexes:
  - (dataset, -created_at)
  - (status)

Methods:
  - mark_completed(predictions, statistics)
  - mark_failed(error_message)
```

### 5. Core Utilities (`core/`)

**Components**:

#### `exceptions.py`
- `BaseAPIException`: Base exception class
- `ValidationError`: Data validation failure
- `CSVParsingError`: CSV parsing failure
- `MissingColumnsError`: Missing required columns
- `InvalidDataError`: Invalid data values
- `NotFoundError`: Resource not found
- `ConflictError`: Resource conflict
- `ServerError`: Internal server error
- `custom_exception_handler()`: DRF exception handler

#### `response.py`
- `APIResponse.success()`: Successful response
- `APIResponse.created()`: 201 Created response
- `APIResponse.error()`: Error response
- `APIResponse.paginated()`: Paginated response

#### `pagination.py`
- `StandardResultsSetPagination`: Page-based pagination

## Data Flow

### Upload CSV Workflow
```
Request → UploadCSVView
         ↓
    Validate request data (serializer)
         ↓
    Validate upload constraints (validator)
         ↓
    Create dataset record (DatasetService.create_dataset)
         ↓
    Parse CSV file (CSVParserService.parse_csv)
         ↓
    Validate column presence (CSVParserService.validate_columns)
         ↓
    Validate data integrity (CSVParserService.validate_rows)
         ↓
    Transform to records (CSVParserService.transform_data)
         ↓
    Validate individual records (ValidationService.validate_candlestick)
         ↓
    Bulk insert candlesticks (DatasetService.store_candlesticks)
         ↓
    Finalize dataset (DatasetService.finalize_dataset)
         ↓
    Return 201 Created response
```

### Prediction Workflow
```
Request → PredictionView
       ↓
  Validate request data
       ↓
  Verify dataset exists
       ↓
  Create prediction record
       ↓
  Retrieve historical candlesticks
       ↓
  Run forecasting model (async task)
       ↓
  Store predictions and metrics
       ↓
  Return response with predictions
```

## Database Schema

### Entity Relationships
```
UploadedDataset
    ├── 1:N CandlestickData
    │   └── Historical OHLCV data for the dataset
    └── 1:N PredictionResult
        └── Forecast results for the dataset
```

### Indexing Strategy
```
UploadedDataset:
  - (symbol, -created_at) - Query by symbol with recent first
  - (status) - Filter by dataset status

CandlestickData:
  - (dataset, timestamp) - Query candlesticks for dataset
  - (timestamp) - Range queries on time

PredictionResult:
  - (dataset, -created_at) - Recent predictions for dataset
  - (status) - Filter by prediction status
```

## Error Handling

### Exception Hierarchy
```
Exception
└── APIException (DRF)
    ├── BaseAPIException
    │   ├── ValidationError
    │   │   ├── CSVParsingError
    │   │   │   └── MissingColumnsError
    │   │   └── InvalidDataError
    │   ├── NotFoundError
    │   ├── ConflictError
    │   └── ServerError
```

### Response Formats

**Success Response**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

**Error Response**
```json
{
  "success": false,
  "message": "Error description",
  "code": "error_code",
  "errors": {"field": ["error detail"]}
}
```

## Configuration

### Settings Module (`config/settings.py`)
- Environment variables via `.env`
- Database configuration
- REST Framework settings
- JWT authentication
- CORS policy
- Logging configuration
- File upload limits

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', 'db.sqlite3'),
        # PostgreSQL: uncomment for production
        # 'USER': os.getenv('DB_USER'),
        # 'PASSWORD': os.getenv('DB_PASSWORD'),
        # 'HOST': os.getenv('DB_HOST'),
        # 'PORT': os.getenv('DB_PORT'),
    }
}
```

### REST Framework Configuration
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}
```

## Testing

### Test Structure
```
forecasting/tests/
├── __init__.py
└── test_api.py
    ├── CSVUploadTestCase
    │   ├── test_upload_valid_csv()
    │   └── test_upload_missing_columns()
    ├── HealthCheckTestCase
    │   └── test_health_check()
```

### Running Tests
```bash
# All tests
python manage.py test forecasting.tests

# Specific test class
python manage.py test forecasting.tests.CSVUploadTestCase

# Specific test method
python manage.py test forecasting.tests.CSVUploadTestCase.test_upload_valid_csv

# With verbose output
python manage.py test forecasting.tests --verbosity=2
```

## Performance Considerations

### Database Optimization
- **Bulk Insert**: CandlestickData created with `bulk_create()` for performance
- **Batch Size**: 1000 records per batch for memory efficiency
- **Indexing**: Strategic indexes on frequently queried columns
- **Connection Pooling**: Configured for PostgreSQL in production

### API Optimization
- **Pagination**: Default 50 items per page, configurable up to 1000
- **Field Selection**: Only required fields returned in list endpoints
- **Caching**: Ready for Django cache framework integration
- **Async Tasks**: Service layer supports async execution (Celery/RQ)

### Limits
- **Max CSV Size**: 10 MB
- **Max Rows**: 100,000 rows per upload
- **Max Pagination**: 1,000 items per page

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Add all domains to `ALLOWED_HOSTS`
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS origins
- [ ] Enable request logging
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backups
- [ ] Run `python manage.py collectstatic`
- [ ] Run migrations on production database

### Deployment Options
- **Docker**: Container deployment with docker-compose
- **Gunicorn**: Production WSGI server
- **Nginx**: Reverse proxy and load balancing
- **Heroku**: Platform-as-a-Service deployment
- **AWS/Azure**: Cloud platform deployment

## Future Enhancements

- [ ] Async task queue (Celery) for forecasting
- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Dataset versioning
- [ ] Prediction comparison tools
- [ ] Model performance analytics
- [ ] API rate limiting
- [ ] Request/response caching
- [ ] GraphQL API layer
- [ ] OpenAPI/Swagger documentation

