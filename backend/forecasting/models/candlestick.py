"""
Database models for candlestick data and predictions.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class UploadedDataset(models.Model):
    """
    Represents an uploaded dataset of historical candlestick data.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('validated', 'Validated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Dataset metadata
    symbol = models.CharField(max_length=20, help_text="Stock symbol or trading pair (e.g., AAPL, BTC/USD)")
    timeframe = models.CharField(
        max_length=10,
        default='1d',
        help_text="Candlestick timeframe (e.g., 1m, 5m, 1h, 1d)"
    )
    source = models.CharField(
        max_length=100,
        default='user_upload',
        help_text="Data source identifier"
    )
    filename = models.CharField(max_length=255, help_text="Original filename")

    # Data statistics
    rows_count = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    date_from = models.DateTimeField(null=True, blank=True)
    date_to = models.DateTimeField(null=True, blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    validation_errors = models.JSONField(default=dict, blank=True, help_text="Validation error details")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['symbol', '-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Uploaded Dataset'
        verbose_name_plural = 'Uploaded Datasets'

    def __str__(self) -> str:
        return f"{self.symbol} {self.timeframe} - {self.rows_count} rows ({self.status})"

    def mark_validated(self) -> None:
        """Mark dataset as validated."""
        self.status = 'validated'
        self.save(update_fields=['status', 'updated_at'])

    def mark_failed(self, errors: dict) -> None:
        """Mark dataset as failed with error details."""
        self.status = 'failed'
        self.validation_errors = errors
        self.save(update_fields=['status', 'validation_errors', 'updated_at'])


class CandlestickData(models.Model):
    """
    Individual candlestick records from uploaded datasets.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        UploadedDataset,
        on_delete=models.CASCADE,
        related_name='candlesticks',
    )

    # Candlestick OHLCV data
    timestamp = models.DateTimeField(db_index=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=8, validators=[MinValueValidator(0)])
    high_price = models.DecimalField(max_digits=15, decimal_places=8, validators=[MinValueValidator(0)])
    low_price = models.DecimalField(max_digits=15, decimal_places=8, validators=[MinValueValidator(0)])
    close_price = models.DecimalField(max_digits=15, decimal_places=8, validators=[MinValueValidator(0)])
    volume = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])

    # Computed fields
    high_low_diff = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="High - Low"
    )
    close_open_diff = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Close - Open"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['dataset', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = 'Candlestick Data'
        verbose_name_plural = 'Candlestick Data'
        unique_together = [['dataset', 'timestamp']]

    def __str__(self) -> str:
        return f"{self.dataset.symbol} {self.timestamp}"

    def save(self, *args, **kwargs) -> None:
        """Calculate derived fields before saving."""
        if self.high_price and self.low_price:
            self.high_low_diff = self.high_price - self.low_price
        if self.close_price and self.open_price:
            self.close_open_diff = self.close_price - self.open_price
        super().save(*args, **kwargs)


class PredictionResult(models.Model):
    """
    Stores prediction results and metadata.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        UploadedDataset,
        on_delete=models.CASCADE,
        related_name='predictions',
    )

    # Prediction parameters
    model_name = models.CharField(
        max_length=100,
        default='default',
        help_text="Name of the forecasting model used"
    )
    horizon = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of periods to forecast"
    )
    confidence_level = models.FloatField(
        default=0.95,
        validators=[MinValueValidator(0), MinValueValidator(1)],
        help_text="Confidence level (0-1)"
    )

    # Prediction data
    predictions = models.JSONField(
        default=list,
        help_text="Array of predicted values with timestamps"
    )
    statistics = models.JSONField(
        default=dict,
        help_text="Prediction statistics (RMSE, MAE, etc.)"
    )

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, help_text="Error details if processing failed")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dataset', '-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Prediction Result'
        verbose_name_plural = 'Prediction Results'

    def __str__(self) -> str:
        return f"Prediction for {self.dataset.symbol} - {self.horizon} periods ({self.status})"

    def mark_completed(self, predictions: list, statistics: dict) -> None:
        """Mark prediction as completed with results."""
        self.status = 'completed'
        self.predictions = predictions
        self.statistics = statistics
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'predictions', 'statistics', 'completed_at', 'updated_at'])

    def mark_failed(self, error_message: str) -> None:
        """Mark prediction as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

