"""
API validators for request data.
"""

from typing import Dict, Any

from core.exceptions import ValidationError


class UploadValidator:
    """Validator for CSV upload requests."""

    @staticmethod
    def validate_upload_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate upload request data.

        Args:
            data: Request data dictionary

        Returns:
            Validated data

        Raises:
            ValidationError: If validation fails
        """
        if 'file' not in data or not data['file']:
            raise ValidationError("File is required")

        if 'symbol' not in data or not data['symbol']:
            raise ValidationError("Symbol is required")

        symbol = data['symbol'].strip()
        if len(symbol) > 20 or len(symbol) < 1:
            raise ValidationError("Symbol must be between 1 and 20 characters")

        timeframe = data.get('timeframe', '1d').strip()
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
        if timeframe not in valid_timeframes:
            raise ValidationError(
                f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
            )

        return data


class PredictionValidator:
    """Validator for prediction requests."""

    @staticmethod
    def validate_prediction_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate prediction request data.

        Args:
            data: Request data dictionary

        Returns:
            Validated data

        Raises:
            ValidationError: If validation fails
        """
        if 'dataset_id' not in data or not data['dataset_id']:
            raise ValidationError("dataset_id is required")

        horizon = data.get('horizon', 30)
        if not isinstance(horizon, int) or horizon < 1 or horizon > 365:
            raise ValidationError("Horizon must be an integer between 1 and 365")

        confidence = data.get('confidence', 0.95)
        if not isinstance(confidence, (int, float)) or confidence <= 0 or confidence >= 1:
            raise ValidationError("Confidence must be a float between 0 and 1")

        return data

