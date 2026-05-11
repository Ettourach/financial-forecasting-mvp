# Financial Forecasting MVP

> **AI-powered financial forecasting platform** for uploading historical candlestick CSV data, processing market patterns with machine learning workflows, and visualizing forward-looking predictions in an interactive dashboard.

---

## Overview

**Financial Forecasting MVP** is a startup-grade financial analytics platform designed for market data ingestion, forecast generation, and decision-support visualization.

The product is built around a modern two-layer application model:

- a **Django + Django REST Framework backend** for data ingestion, validation, persistence, and prediction APIs
- a **Streamlit frontend** for interactive analytics, charting, and forecast exploration

The roadmap includes **Kronos model integration** for advanced forecasting, with a design that supports future model swaps, scalable storage, and production deployment.

---

## Project Banner

```text
┌──────────────────────────────────────────────────────────────────────┐
│                Financial Forecasting MVP                             │
│  Historical Candles  →  AI Forecasting  →  Interactive Market Views   │
│                                                                      │
│  Stack: Django • DRF • PostgreSQL • Streamlit • Pandas • Plotly       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

- Upload historical candlestick CSV files
- Validate and normalize market data before forecasting
- Persist datasets and predictions in PostgreSQL
- Generate time-series forecasts through a modular pipeline
- Visualize price trends, predicted ranges, and signal overlays
- Expose backend APIs for programmatic integration
- Designed for future Kronos model integration
- Ready for containerized deployment with Docker

---

## Architecture

### High-Level Flow

```text
CSV Upload → Validation → Feature Engineering → Forecast Service → Database → API Response → Streamlit Dashboard
```

### Backend Architecture

The backend is organized to keep business logic isolated and maintainable:

- **API layer**: Django REST Framework endpoints handle uploads, prediction requests, and result retrieval.
- **Serializers**: Validate request payloads, enforce schema rules, and convert Python objects to JSON.
- **Models**: Store uploaded datasets, prediction jobs, forecast outputs, and related metadata.
- **Service layer**: Contains forecasting orchestration, preprocessing, feature engineering, and model execution.
- **Forecasting pipeline**: Converts raw candlestick data into structured features, generates predictions, and formats output for downstream consumers.
- **Database flow**: Ingested records are written to PostgreSQL, then linked to prediction artifacts for auditability and repeatability.

### Data Flow

1. User uploads a CSV file.
2. Backend validates required columns and time ordering.
3. Data is cleaned, normalized, and prepared for the forecasting pipeline.
4. The service layer runs prediction logic.
5. Output is persisted to the database.
6. Streamlit queries the API and renders the forecast dashboard.

---

## Tech Stack

### Core

- **Python** — application runtime and analytics layer
- **Django** — backend framework
- **Django REST Framework** — API development
- **PostgreSQL** — primary relational database
- **Streamlit** — interactive dashboard interface

### Data & Analytics

- **Pandas** — data ingestion and transformation
- **NumPy** — numerical operations
- **Plotly** — interactive charting and visualization

### Deployment & Infrastructure

- **Docker** — containerization
- **Hugging Face Spaces** — frontend/demo hosting option
- **Gunicorn / Uvicorn** — production-grade application serving

---

## Folder Structure

```text
backend/
frontend/
docs/
requirements.txt
README.md
```

### `backend/`
Contains the Django application, REST API endpoints, models, serializers, services, and database integration logic. This is the system of record for uploads, forecasts, and application state.

### `frontend/`
Hosts the Streamlit application responsible for user interaction, chart rendering, forecast exploration, and dashboard-level UX.

### `docs/`
Reserved for product documentation, API notes, architecture diagrams, and deployment references.

### `requirements.txt`
Python dependency manifest for local development, CI, and reproducible deployments.

### `README.md`
Primary project documentation for contributors, recruiters, clients, and deployment stakeholders.

---

## Installation Guide

### 1) Clone the repository

```bash
git clone <repository-url>
cd financial-forecasting-mvp
```

### 2) Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_forecasting
SECRET_KEY=replace-with-a-secure-django-secret
DEBUG=True
JWT_SECRET=replace-with-a-jwt-secret
```

### 5) Set up PostgreSQL

Create a database and user for the application:

```bash
psql -U postgres -c "CREATE DATABASE financial_forecasting;"
psql -U postgres -c "CREATE USER financial_user WITH PASSWORD 'strong_password';"
psql -U postgres -c "ALTER ROLE financial_user SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE financial_user SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE financial_user SET timezone TO 'UTC';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE financial_forecasting TO financial_user;"
```

### 6) Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7) Start the Django backend

```bash
python manage.py runserver
```

### 8) Start the Streamlit frontend

```bash
streamlit run frontend/app.py
```

> If your local entrypoint uses a different module name, update the command to match the actual Streamlit script.

---

## Environment Setup

The application expects the following environment variables:

```env
DATABASE_URL=
SECRET_KEY=
DEBUG=
JWT_SECRET=
```

### Suggested local values

- `DEBUG=True` for development
- `DEBUG=False` in production
- Store secrets in environment variables or a secure secret manager
- Use separate PostgreSQL credentials for development and production

---

## PostgreSQL Setup

Recommended production configuration:

- Use a dedicated database instance
- Enable regular backups and point-in-time recovery if available
- Restrict network access to trusted application hosts
- Use separate roles for migration/admin access and runtime access
- Configure connection pooling for scale

Example Django configuration through `DATABASE_URL`:

```env
DATABASE_URL=postgresql://financial_user:strong_password@localhost:5432/financial_forecasting
```

---

## API Overview

The API is designed to support both UI-driven and programmatic forecasting workflows.

### Expected Endpoints

- `POST /api/upload/` — upload historical candlestick CSV data
- `POST /api/predict/` — generate a forecast from uploaded or referenced data
- `GET /api/predictions/` — retrieve prediction history
- `GET /api/health/` — service health check

> Endpoint paths can be versioned later, for example `/api/v1/...`.

---

## API Examples

### 1) Upload Endpoint

**Request**

```http
POST /api/upload/
Content-Type: multipart/form-data
```

```json
{
  "symbol": "AAPL",
  "timeframe": "1d",
  "file": "candles.csv"
}
```

**Example CSV columns**

```csv
timestamp,open,high,low,close,volume
2024-01-01,185.10,187.30,184.20,186.50,54122000
2024-01-02,186.40,188.10,185.00,187.80,49345000
```

**Response**

```json
{
  "message": "File uploaded successfully",
  "dataset_id": "ds_8f2a91",
  "rows_processed": 2450,
  "symbol": "AAPL",
  "status": "validated"
}
```

### 2) Prediction Endpoint

**Request**

```http
POST /api/predict/
Content-Type: application/json
```

```json
{
  "dataset_id": "ds_8f2a91",
  "horizon": 30,
  "model": "kronos"
}
```

**Response**

```json
{
  "prediction_id": "pred_1042c7",
  "dataset_id": "ds_8f2a91",
  "model": "kronos",
  "horizon": 30,
  "forecast": [
	{"date": "2024-02-01", "predicted_close": 188.42},
	{"date": "2024-02-02", "predicted_close": 189.08}
  ],
  "confidence": 0.87,
  "status": "completed"
}
```

---

## Running the Application

### Backend

```bash
python manage.py runserver
```

### Frontend

```bash
streamlit run frontend/app.py
```

### Production-style deployment

For production, the backend should run behind a WSGI/ASGI server and the frontend should be deployed separately or containerized with the API gateway.

---

## Deployment

### Docker

This project is suitable for Docker-based deployment with separate containers for:

- Django backend
- Streamlit frontend
- PostgreSQL database

Recommended production characteristics:

- environment-based configuration
- health checks
- persistent database volumes
- secure secret management
- non-root containers where possible

### Hugging Face Spaces

The Streamlit frontend can be deployed to **Hugging Face Spaces** for fast demo delivery and stakeholder review.

Recommended usage:

- host the dashboard UI on Spaces
- connect the frontend to a deployed API backend
- use environment variables for API base URLs and secrets

### Production Configuration

- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Use managed PostgreSQL in production
- Enable request logging and error monitoring
- Apply CORS and CSRF settings appropriately
- Restrict API access if authentication is enabled

---

## Future Roadmap

- **Kronos integration** for more advanced time-series forecasting
- **Real-time forecasting** for live market streams
- **Authentication and authorization** for secure user access
- **Dashboard analytics** with model performance, error bands, and trend insights
- **SaaS scalability** for multi-tenant deployment and subscription workflows
- **Alerting and notifications** for threshold-based market signals
- **Model governance** for experiment tracking and versioned predictions

---

## Contributing

Contributions are welcome.

### Suggested workflow

1. Fork the repository
2. Create a feature branch
3. Make focused changes with clear commit messages
4. Add or update documentation where needed
5. Open a pull request with a concise summary

### Good contribution areas

- forecasting pipeline improvements
- API hardening and validation
- Streamlit UX enhancements
- PostgreSQL schema design
- deployment automation

---

## License

This project is licensed under the terms of the repository `LICENSE` file.

---

## Contact / Project Notes

This repository is structured as an MVP foundation for a modern financial forecasting product. As the implementation evolves, the README should be updated to reflect:

- the exact API routes
- deployed environment URLs
- data schema changes
- model versions and performance metrics

