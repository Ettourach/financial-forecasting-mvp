"""
API views for forecasting endpoints.
"""

import logging
from uuid import UUID

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from core.response import APIResponse
from core.exceptions import NotFoundError, ServerError
from forecasting.serializers.candlestick import (
    CSVUploadSerializer,
    UploadedDatasetSerializer,
    CandlestickDataListSerializer,
    PredictionRequestSerializer,
    PredictionResultDetailSerializer,
)
from forecasting.models.candlestick import UploadedDataset, CandlestickData
from forecasting.services.csv_parser import CSVParserService
from forecasting.services.dataset import DatasetService
from forecasting.services.validation import ValidationService
from .validators import UploadValidator, PredictionValidator

logger = logging.getLogger(__name__)


class UploadCSVView(APIView):
    """
    API endpoint for uploading candlestick CSV data.

    POST /api/upload/
    - Accepts CSV file with candlestick data
    - Validates data structure and values
    - Stores candlesticks in PostgreSQL
    """

    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """Handle CSV file upload."""
        try:
            # Validate request data
            serializer = CSVUploadSerializer(data=request.data)
            if not serializer.is_valid():
                return APIResponse.error(
                    message="Validation failed",
                    errors=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data
            UploadValidator.validate_upload_request(validated_data)

            # Extract file and metadata
            file = validated_data['file']
            symbol = validated_data['symbol'].upper()
            timeframe = validated_data.get('timeframe', '1d')
            source = validated_data.get('source', 'user_upload')

            logger.info(f"Processing upload: {symbol} {timeframe}")

            # Create dataset record
            dataset = DatasetService.create_dataset(
                symbol=symbol,
                timeframe=timeframe,
                filename=file.name,
                source=source,
            )

            # Parse and validate CSV
            df, records = CSVParserService.process_csv_file(file)

            # Store candlesticks
            count, errors = DatasetService.store_candlesticks(dataset, records)

            # Finalize dataset
            DatasetService.finalize_dataset(dataset, records)

            logger.info(f"Successfully uploaded {count} candlesticks for dataset {dataset.id}")

            return APIResponse.created(
                message="Dataset uploaded successfully",
                data={
                    "dataset_id": str(dataset.id),
                    "symbol": dataset.symbol,
                    "timeframe": dataset.timeframe,
                    "rows_processed": count,
                    "date_from": dataset.date_from.isoformat() if dataset.date_from else None,
                    "date_to": dataset.date_to.isoformat() if dataset.date_to else None,
                    "status": dataset.status,
                }
            )

        except Exception as e:
            logger.exception(f"Upload error: {str(e)}")
            raise


class DatasetDetailView(APIView):
    """
    API endpoint for viewing dataset details.

    GET /api/datasets/{dataset_id}/
    """

    permission_classes = [AllowAny]

    def get(self, request, dataset_id):
        """Retrieve dataset details."""
        try:
            dataset = DatasetService.get_dataset_by_id(UUID(dataset_id))
            if not dataset:
                raise NotFoundError(f"Dataset {dataset_id} not found")

            serializer = UploadedDatasetSerializer(dataset)

            # Add statistics
            stats = DatasetService.get_dataset_statistics(dataset.id)

            return APIResponse.success(
                message="Dataset retrieved successfully",
                data={
                    **serializer.data,
                    "statistics": stats,
                }
            )

        except ValueError:
            raise NotFoundError("Invalid dataset ID format")
        except Exception as e:
            logger.exception(f"Error retrieving dataset: {str(e)}")
            raise


class DatasetCandlesticksView(APIView):
    """
    API endpoint for viewing candlestick data.

    GET /api/datasets/{dataset_id}/candlesticks/
    """

    permission_classes = [AllowAny]

    def get(self, request, dataset_id):
        """Retrieve candlesticks for a dataset."""
        try:
            dataset = DatasetService.get_dataset_by_id(UUID(dataset_id))
            if not dataset:
                raise NotFoundError(f"Dataset {dataset_id} not found")

            # Get limit from query params
            limit = int(request.query_params.get('limit', 1000))
            limit = min(limit, 10000)  # Cap at 10000

            candlesticks = CandlestickData.objects.filter(
                dataset_id=UUID(dataset_id)
            ).order_by('timestamp').values(
                'id', 'timestamp', 'open_price', 'high_price',
                'low_price', 'close_price', 'volume'
            )[:limit]

            return APIResponse.success(
                message="Candlesticks retrieved successfully",
                data={
                    "dataset_id": str(dataset.id),
                    "symbol": dataset.symbol,
                    "timeframe": dataset.timeframe,
                    "count": len(list(candlesticks)),
                    "candlesticks": list(candlesticks),
                }
            )

        except ValueError:
            raise NotFoundError("Invalid dataset ID format")
        except Exception as e:
            logger.exception(f"Error retrieving candlesticks: {str(e)}")
            raise


class PredictionView(APIView):
    """
    API endpoint for generating predictions.

    POST /api/predict/
    - Accepts dataset ID and prediction parameters
    - Generates forecast using forecasting model
    - Returns predictions
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Generate prediction for a dataset."""
        try:
            # Validate request
            serializer = PredictionRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return APIResponse.error(
                    message="Validation failed",
                    errors=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data
            PredictionValidator.validate_prediction_request(validated_data)

            dataset_id = validated_data['dataset_id']
            horizon = validated_data.get('horizon', 30)
            model = validated_data.get('model', 'default')
            confidence = validated_data.get('confidence', 0.95)

            # Verify dataset exists
            dataset = DatasetService.get_dataset_by_id(dataset_id)
            if not dataset:
                raise NotFoundError(f"Dataset {dataset_id} not found")

            logger.info(f"Generating prediction for dataset {dataset_id}")

            # TODO: Implement actual forecasting model
            # For now, return placeholder response
            predictions = [
                {
                    "period": i + 1,
                    "predicted_close": float(dataset.candlesticks.first().close_price) * (1 + (i * 0.001)),
                }
                for i in range(horizon)
            ]

            return APIResponse.created(
                message="Prediction generated successfully",
                data={
                    "dataset_id": str(dataset.id),
                    "symbol": dataset.symbol,
                    "model": model,
                    "horizon": horizon,
                    "confidence": confidence,
                    "predictions": predictions,
                    "status": "completed",
                }
            )

        except Exception as e:
            logger.exception(f"Prediction error: {str(e)}")
            raise


class HealthCheckView(APIView):
    """Health check endpoint."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return health status."""
        return APIResponse.success(
            message="Backend is healthy",
            data={"status": "ok"}
        )


