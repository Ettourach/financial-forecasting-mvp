"""
Serializers for forecasting app models.
"""

from rest_framework import serializers
from forecasting.models.candlestick import (
    UploadedDataset,
    CandlestickData,
    PredictionResult,
)


class UploadedDatasetSerializer(serializers.ModelSerializer):
    """Serializer for UploadedDataset model."""

    class Meta:
        model = UploadedDataset
        fields = [
            'id',
            'symbol',
            'timeframe',
            'source',
            'filename',
            'rows_count',
            'date_from',
            'date_to',
            'status',
            'validation_errors',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'validation_errors']


class CandlestickDataSerializer(serializers.ModelSerializer):
    """Serializer for CandlestickData model."""

    class Meta:
        model = CandlestickData
        fields = [
            'id',
            'dataset',
            'timestamp',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'high_low_diff',
            'close_open_diff',
            'created_at',
        ]
        read_only_fields = ['id', 'high_low_diff', 'close_open_diff', 'created_at']


class CandlestickDataListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing candlestick data."""

    class Meta:
        model = CandlestickData
        fields = [
            'id',
            'timestamp',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
        ]


class PredictionResultSerializer(serializers.ModelSerializer):
    """Serializer for PredictionResult model."""

    class Meta:
        model = PredictionResult
        fields = [
            'id',
            'dataset',
            'model_name',
            'horizon',
            'confidence_level',
            'predictions',
            'statistics',
            'status',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'error_message',
            'predictions',
            'statistics',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class PredictionResultDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PredictionResult."""

    dataset_summary = serializers.SerializerMethodField()

    class Meta:
        model = PredictionResult
        fields = [
            'id',
            'dataset',
            'dataset_summary',
            'model_name',
            'horizon',
            'confidence_level',
            'predictions',
            'statistics',
            'status',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'error_message',
            'predictions',
            'statistics',
            'created_at',
            'updated_at',
            'completed_at',
        ]

    def get_dataset_summary(self, obj) -> dict:
        """Get a summary of the related dataset."""
        dataset = obj.dataset
        return {
            'id': str(dataset.id),
            'symbol': dataset.symbol,
            'timeframe': dataset.timeframe,
            'rows_count': dataset.rows_count,
        }


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file uploads."""

    file = serializers.FileField(
        help_text="CSV file containing candlestick data"
    )
    symbol = serializers.CharField(
        max_length=20,
        help_text="Stock symbol or trading pair (e.g., AAPL)"
    )
    timeframe = serializers.CharField(
        max_length=10,
        default='1d',
        help_text="Candlestick timeframe (e.g., 1m, 5m, 1h, 1d)"
    )
    source = serializers.CharField(
        max_length=100,
        default='user_upload',
        required=False,
    )

    def validate_file(self, value):
        """Validate file is a CSV."""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file.")
        if value.size > 10 * 1024 * 1024:  # 10MB max
            raise serializers.ValidationError("File size must be less than 10MB.")
        return value


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction request."""

    dataset_id = serializers.UUIDField(help_text="ID of the dataset to forecast")
    model = serializers.CharField(
        max_length=100,
        default='default',
        help_text="Forecasting model to use"
    )
    horizon = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of periods to forecast"
    )
    confidence = serializers.FloatField(
        default=0.95,
        min_value=0.0,
        max_value=1.0,
        required=False,
        help_text="Confidence level for prediction intervals"
    )

