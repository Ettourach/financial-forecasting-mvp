"""
Regression tests for Django admin compatibility under the active Python runtime.
"""

import copy

from django.contrib.auth import get_user_model
from django.template.context import Context
from django.test import TestCase, Client


class AdminCompatibilityTestCase(TestCase):
    """Ensure admin templates render after the context copy compatibility shim."""

    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model(
            username="admin",
            email="admin@example.com",
        )
        self.user.set_password("Admin12345!")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

    def test_template_context_copy(self):
        ctx = Context({"foo": "bar"})
        copied = copy.copy(ctx)
        self.assertEqual(copied.dicts, ctx.dicts)

    def test_admin_add_pages_render(self):
        paths = [
            "/admin/auth/user/add/",
            "/admin/auth/group/add/",
            "/admin/forecasting/uploadeddataset/add/",
            "/admin/forecasting/candlestickdata/add/",
            "/admin/forecasting/predictionresult/add/",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

