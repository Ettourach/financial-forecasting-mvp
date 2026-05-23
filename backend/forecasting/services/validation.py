"""
Data validation service.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from core.exceptions import InvalidDataError

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating business logic and constraints."""

    @staticmethod
    def validate_candlestick(record: Dict[str, Any]) -> None:
        """
        Validate a single candlestick record.

        Args:
            record: Candlestick data dictionary

        Raises:
            InvalidDataError: If validation fails
        """
        required_fields = ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']

        for field in required_fields:
            if field not in record:
                raise InvalidDataError(f"Missing required field: {field}")

        # Validate price relationships
        if record['high_price'] < record['low_price']:
            raise InvalidDataError(
                f"High price ({record['high_price']}) must be >= low price ({record['low_price']})"
            )

        if record['high_price'] < record['open_price']:
            raise InvalidDataError(
                f"High price must be >= open price"
            )

        if record['high_price'] < record['close_price']:
            raise InvalidDataError(
                f"High price must be >= close price"
            )

        if record['low_price'] > record['open_price']:
            raise InvalidDataError(
                f"Low price must be <= open price"
            )

        if record['low_price'] > record['close_price']:
            raise InvalidDataError(
                f"Low price must be <= close price"
            )

        # Validate volume
        if record['volume'] < 0:
            raise InvalidDataError("Volume must be non-negative")

    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format."""
        if not symbol or len(symbol) > 20:
            raise InvalidDataError("Invalid symbol format")
        if not symbol.replace('/', '').replace('-', '').isalnum():
            raise InvalidDataError("Symbol contains invalid characters")
        return True

    @staticmethod
    def validate_timeframe(timeframe: str) -> bool:
        """Validate timeframe format."""
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
        if timeframe not in valid_timeframes:
            raise InvalidDataError(f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}")
        return True

    @staticmethod
    def validate_horizon(horizon: int, max_horizon: int = 365) -> bool:
        """Validate prediction horizon."""
        if horizon < 1 or horizon > max_horizon:
            raise InvalidDataError(f"Horizon must be between 1 and {max_horizon}")
        return True

    @staticmethod
    def validate_candlesticks_ordered(records: List[Dict]) -> None:
        """
        Validate that candlesticks are in chronological order.

        Args:
            records: List of candlestick records

        Raises:
            InvalidDataError: If records are not in order
        """
        if len(records) < 2:
            return

        for i in range(1, len(records)):
            prev_ts = records[i - 1]['timestamp']
            curr_ts = records[i]['timestamp']

            if isinstance(prev_ts, str):
                prev_ts = datetime.fromisoformat(prev_ts)
            if isinstance(curr_ts, str):
                curr_ts = datetime.fromisoformat(curr_ts)

            if curr_ts <= prev_ts:
                raise InvalidDataError(
                    f"Candlesticks must be in chronological order. "
                    f"Found {prev_ts} followed by {curr_ts}"
                )

    @staticmethod
    def validate_no_duplicates(records: List[Dict]) -> None:
        """
        Validate that there are no duplicate timestamps.

        Args:
            records: List of candlestick records

        Raises:
            InvalidDataError: If duplicates found
        """
        timestamps = [r['timestamp'] for r in records]
        if len(timestamps) != len(set(timestamps)):
            raise InvalidDataError("Duplicate timestamps found in dataset")

