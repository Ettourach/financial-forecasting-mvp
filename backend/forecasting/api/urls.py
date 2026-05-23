"""
URL routing for forecasting API.
"""

from django.urls import path
from .views import (
    UploadCSVView,
    DatasetDetailView,
    DatasetCandlesticksView,
    PredictionView,
    HealthCheckView,
)

app_name = 'forecasting_api'

urlpatterns = [
    # Upload endpoint
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),

    # Dataset endpoints
    path('datasets/<uuid:dataset_id>/', DatasetDetailView.as_view(), name='dataset_detail'),
    path('datasets/<uuid:dataset_id>/candlesticks/', DatasetCandlesticksView.as_view(), name='dataset_candlesticks'),

    # Prediction endpoint
    path('predict/', PredictionView.as_view(), name='predict'),

    # Health check
    path('health/', HealthCheckView.as_view(), name='health'),
]