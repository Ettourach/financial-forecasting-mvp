"""
Compatibility shims for runtime differences between Django and the active Python version.
"""

from copy import copy


def patch_django_template_context_copy() -> None:
    """Patch Django's template context copy implementation for Python 3.14+."""

    try:
        from django.template.context import BaseContext, Context
    except Exception:
        return

    if getattr(BaseContext.__copy__, "_financial_forecasting_patched", False):
        return

    def _copy_base_context(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        duplicate.dicts = self.dicts[:]
        return duplicate

    def _copy_context(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        duplicate.dicts = self.dicts[:]
        duplicate.render_context = copy(self.render_context)
        return duplicate

    _copy_base_context._financial_forecasting_patched = True
    _copy_context._financial_forecasting_patched = True

    BaseContext.__copy__ = _copy_base_context
    Context.__copy__ = _copy_context


