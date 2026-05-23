"""
Dataset operations service.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from forecasting.models.candlestick import (
    UploadedDataset,
    CandlestickData,
)
from .validation import ValidationService

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for managing datasets and candlestick data."""

    @staticmethod
    @transaction.atomic
    def create_dataset(
        symbol: str,
        timeframe: str,
        filename: str,
        source: str = 'user_upload',
    ) -> UploadedDataset:
        """
        Create a new dataset record.

        Args:
            symbol: Trading symbol
            timeframe: Candlestick timeframe
            filename: Original filename
            source: Data source identifier

        Returns:
            Created UploadedDataset instance
        """
        ValidationService.validate_symbol(symbol)
        ValidationService.validate_timeframe(timeframe)

        dataset = UploadedDataset(
            symbol=symbol,
            timeframe=timeframe,
            filename=filename,
            source=source,
            status='pending',
        )
        dataset.save()
        logger.info(f"Created dataset {dataset.id} for {symbol}")
        return dataset

    @staticmethod
    @transaction.atomic
    def store_candlesticks(
        dataset: UploadedDataset,
        records: List[Dict[str, Any]],
    ) -> Tuple[int, List[str]]:
        """
        Store candlestick records in the database.

        Args:
            dataset: UploadedDataset instance
            records: List of candlestick records

        Returns:
            Tuple of (count_created, errors)
        """
        # Validate records
        ValidationService.validate_candlesticks_ordered(records)
        ValidationService.validate_no_duplicates(records)

        # Validate individual records
        for record in records:
            ValidationService.validate_candlestick(record)

        # Bulk create candlesticks
        candlesticks = []
        for record in records:
            candlestick = CandlestickData(
                dataset=dataset,
                timestamp=record['timestamp'],
                open_price=record['open_price'],
                high_price=record['high_price'],
                low_price=record['low_price'],
                close_price=record['close_price'],
                volume=record['volume'],
            )
            candlesticks.append(candlestick)

        created = CandlestickData.objects.bulk_create(candlesticks, batch_size=1000)
        logger.info(f"Stored {len(created)} candlesticks for dataset {dataset.id}")

        return len(created), []

    @staticmethod
    @transaction.atomic
    def finalize_dataset(
        dataset: UploadedDataset,
        records: List[Dict[str, Any]],
    ) -> None:
        """
        Finalize dataset after processing.

        Args:
            dataset: UploadedDataset instance
            records: List of processed candlestick records
        """
        if records:
            timestamps = [r['timestamp'] for r in records]
            dataset.date_from = min(timestamps)
            dataset.date_to = max(timestamps)
            dataset.rows_count = len(records)
            dataset.status = 'validated'

        dataset.save(update_fields=['date_from', 'date_to', 'rows_count', 'status', 'updated_at'])
        logger.info(f"Finalized dataset {dataset.id}: {len(records)} rows")

    @staticmethod
    def get_dataset_candlesticks(dataset_id: UUID, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve candlesticks for a dataset.

        Args:
            dataset_id: Dataset UUID
            limit: Maximum number of records to return

        Returns:
            List of candlestick dictionaries
        """
        candlesticks = CandlestickData.objects.filter(
            dataset_id=dataset_id
        ).values(
            'timestamp',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume'
        ).order_by('timestamp')[:limit]

        return list(candlesticks)

    @staticmethod
    def get_dataset_statistics(dataset_id: UUID) -> Dict[str, Any]:
        """
        Calculate statistics for a dataset.

        Args:
            dataset_id: Dataset UUID

        Returns:
            Statistics dictionary
        """
        candlesticks = CandlestickData.objects.filter(
            dataset_id=dataset_id
        ).values_list(
            'close_price',
            'volume',
        )

        if not candlesticks:
            return {}

        close_prices = [float(c[0]) for c in candlesticks]
        volumes = [float(c[1]) for c in candlesticks]

        return {
            'mean_price': sum(close_prices) / len(close_prices),
            'min_price': min(close_prices),
            'max_price': max(close_prices),
            'total_volume': sum(volumes),
            'avg_volume': sum(volumes) / len(volumes),
            'count': len(close_prices),
        }

    @staticmethod
    def delete_dataset_cascade(dataset_id: UUID) -> None:
        """
        Delete a dataset and all related records.

        Args:
            dataset_id: Dataset UUID
        """
        dataset = UploadedDataset.objects.get(id=dataset_id)
        dataset.delete()
        logger.info(f"Deleted dataset {dataset_id} and all related records")

    @staticmethod
    def check_dataset_exists(dataset_id: UUID) -> bool:
        """Check if dataset exists."""
        return UploadedDataset.objects.filter(id=dataset_id).exists()

    @staticmethod
    def get_dataset_by_id(dataset_id: UUID) -> Optional[UploadedDataset]:
        """Get dataset by ID."""
        return UploadedDataset.objects.filter(id=dataset_id).first()

