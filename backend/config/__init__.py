"""
Django configuration package for the Financial Forecasting MVP backend.
"""

from .compat import patch_django_template_context_copy

patch_django_template_context_copy()

