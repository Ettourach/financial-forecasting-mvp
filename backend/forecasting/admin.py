"""
Django admin configuration for forecasting models.
"""

from django.contrib import admin
from forecasting.models.candlestick import (
    UploadedDataset,
    CandlestickData,
    PredictionResult,
)


@admin.register(UploadedDataset)
class UploadedDatasetAdmin(admin.ModelAdmin):
    """Admin for UploadedDataset model."""

    list_display = ['symbol', 'timeframe', 'rows_count', 'status', 'created_at']
    list_filter = ['status', 'timeframe', 'created_at']
    search_fields = ['symbol', 'filename']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identifiers', {'fields': ('id',)}),
        ('Metadata', {'fields': ('symbol', 'timeframe', 'source', 'filename')}),
        ('Statistics', {'fields': ('rows_count', 'date_from', 'date_to')}),
        ('Status', {'fields': ('status', 'validation_errors')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CandlestickData)
class CandlestickDataAdmin(admin.ModelAdmin):
    """Admin for CandlestickData model."""

    list_display = ['timestamp', 'dataset', 'close_price', 'volume']
    list_filter = ['dataset', 'timestamp']
    search_fields = ['dataset__symbol']
    readonly_fields = ['id', 'created_at', 'high_low_diff', 'close_open_diff']
    ordering = ['-timestamp']

    fieldsets = (
        ('Identifiers', {'fields': ('id', 'dataset')}),
        ('OHLCV Data', {
            'fields': (
                'timestamp',
                'open_price',
                'high_price',
                'low_price',
                'close_price',
                'volume'
            ),
        }),
        ('Derived Fields', {'fields': ('high_low_diff', 'close_open_diff')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    """Admin for PredictionResult model."""

    list_display = ['id', 'dataset', 'model_name', 'horizon', 'status', 'created_at']
    list_filter = ['status', 'model_name', 'created_at']
    search_fields = ['dataset__symbol']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identifiers', {'fields': ('id', 'dataset')}),
        ('Configuration', {'fields': ('model_name', 'horizon', 'confidence_level')}),
        ('Results', {'fields': ('predictions', 'statistics')}),
        ('Status', {'fields': ('status', 'error_message')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'completed_at')}),
    )

