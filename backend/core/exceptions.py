"""
Custom exception classes for the Financial Forecasting API.
"""

import logging
from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BaseAPIException(APIException):
    """Base exception for all API errors."""

    def __init__(
        self,
        detail: str = "An error occurred",
        code: str = "error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        self.extra_data = extra_data or {}
        super().__init__(detail=detail, code=code)


class ValidationError(BaseAPIException):
    """Validation error - invalid data provided."""

    def __init__(self, detail: str = "Validation failed", extra_data: Optional[Dict] = None):
        super().__init__(
            detail=detail,
            code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST,
            extra_data=extra_data,
        )


class CSVParsingError(ValidationError):
    """Error parsing CSV file."""

    def __init__(self, detail: str = "Failed to parse CSV file", extra_data: Optional[Dict] = None):
        super().__init__(detail=detail, extra_data=extra_data)


class MissingColumnsError(CSVParsingError):
    """Required columns missing from CSV."""

    def __init__(self, missing_columns: list):
        detail = f"Missing required columns: {', '.join(missing_columns)}"
        extra_data = {"missing_columns": missing_columns}
        super().__init__(detail=detail, extra_data=extra_data)


class InvalidDataError(ValidationError):
    """Invalid data format or values."""

    def __init__(self, detail: str = "Invalid data", extra_data: Optional[Dict] = None):
        super().__init__(detail=detail, extra_data=extra_data)


class NotFoundError(BaseAPIException):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            detail=detail,
            code="not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(BaseAPIException):
    """Resource conflict."""

    def __init__(self, detail: str = "Conflict occurred"):
        super().__init__(
            detail=detail,
            code="conflict",
            status_code=status.HTTP_409_CONFLICT,
        )


class ServerError(BaseAPIException):
    """Internal server error."""

    def __init__(self, detail: str = "Internal server error", extra_data: Optional[Dict] = None):
        logger.error(f"Server error: {detail}")
        super().__init__(
            detail=detail,
            code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            extra_data=extra_data,
        )


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.

    Converts all exceptions to a standardized response format.
    """

    if isinstance(exc, BaseAPIException):
        data = {
            "success": False,
            "message": exc.detail,
            "code": exc.code,
        }
        if exc.extra_data:
            data["errors"] = exc.extra_data

        return Response(data, status=exc.status_code)

    if isinstance(exc, APIException):
        data = {
            "success": False,
            "message": str(exc.detail),
            "code": "api_error",
        }
        return Response(data, status=exc.status_code)

    # Unhandled exceptions
    logger.exception(f"Unhandled exception: {str(exc)}")
    data = {
        "success": False,
        "message": "An unexpected error occurred",
        "code": "server_error",
    }
    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

