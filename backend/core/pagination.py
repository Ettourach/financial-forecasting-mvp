"""
Pagination utilities for API responses.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for list endpoints."""

    page_size = 50
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results to return per page.'
    max_page_size = 1000
    page_query_description = 'A page number within the paginated result set.'

    def get_paginated_response(self, data):
        """Override to use standardized response format."""
        from .response import APIResponse

        return APIResponse.paginated(
            data=data,
            count=self.page.paginator.count,
            page=self.page.number,
            page_size=self.page_size,
        )

