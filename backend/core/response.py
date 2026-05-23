"""
Standard response formatter for API responses.
"""

from typing import Any, Dict, Optional

from rest_framework.response import Response
from rest_framework import status as http_status


class APIResponse:
    """Standardized API response formatter."""

    @staticmethod
    def success(
        message: str = "Success",
        data: Optional[Dict[str, Any]] = None,
        status: int = http_status.HTTP_200_OK,
        **kwargs
    ) -> Response:
        """
        Return a successful response.

        Args:
            message: Response message
            data: Response data payload
            status: HTTP status code
            **kwargs: Additional data to include

        Returns:
            DRF Response object
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data or {},
        }
        response_data.update(kwargs)
        return Response(response_data, status=status)

    @staticmethod
    def created(message: str = "Resource created", data: Optional[Dict] = None, **kwargs) -> Response:
        """Return a 201 Created response."""
        return APIResponse.success(
            message=message,
            data=data,
            status=http_status.HTTP_201_CREATED,
            **kwargs
        )

    @staticmethod
    def error(
        message: str = "Error",
        errors: Optional[Dict[str, Any]] = None,
        status: int = http_status.HTTP_400_BAD_REQUEST,
        **kwargs
    ) -> Response:
        """
        Return an error response.

        Args:
            message: Error message
            errors: Dictionary of errors
            status: HTTP status code
            **kwargs: Additional data to include

        Returns:
            DRF Response object
        """
        response_data = {
            "success": False,
            "message": message,
        }
        if errors:
            response_data["errors"] = errors
        response_data.update(kwargs)
        return Response(response_data, status=status)

    @staticmethod
    def paginated(
        data: list,
        count: int,
        page: int,
        page_size: int,
        message: str = "Success",
        **kwargs
    ) -> Response:
        """
        Return a paginated response.

        Args:
            data: List of items
            count: Total count
            page: Current page number
            page_size: Items per page
            message: Response message
            **kwargs: Additional data

        Returns:
            DRF Response object
        """
        total_pages = (count + page_size - 1) // page_size
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "count": count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            },
        }
        response_data.update(kwargs)
        return Response(response_data, status=http_status.HTTP_200_OK)

