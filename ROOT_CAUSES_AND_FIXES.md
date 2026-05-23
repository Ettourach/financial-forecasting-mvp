# Root Causes & Fix Summary

This document summarizes the root causes discovered while troubleshooting the
`ModuleNotFoundError: No module named 'forecasting.views'` and the subsequent
Django admin rendering failures, and lists the fixes I applied to resolve them.

Date: 2026-05-23
Project: Financial Forecasting MVP (backend)

---

## Executive summary

Two distinct problems occurred:

1. A broken import path in the project URL configuration which caused
   `ModuleNotFoundError: No module named 'forecasting.views'` during server start.

2. A runtime compatibility issue when rendering Django admin templates. The
   failure occurred in `django.template.context.BaseContext.__copy__` under the
   current runtime (Python and Django combination). This produced repeated 500
   errors when loading admin "add" pages.

Both problems are fixed in the repository with minimal, well-scoped changes.

---

## Root cause 1 — Invalid import path (logical / code organization)

Symptoms:
- `ModuleNotFoundError: No module named 'forecasting.views'` on startup.

Why it happened:
- `backend/config/urls.py` attempted to import `from forecasting.views import home`.
- The project organizes DRF views under `forecasting/api/views.py`, not
  `forecasting/views.py`. There is no `forecasting/views.py` module.

Files involved:
- `backend/config/urls.py` (imported `forecasting.views`)
- `backend/forecasting/api/views.py` (actual views live here)

Fix applied:
- Replaced the bad import and improved routing in `backend/config/urls.py`.
  - Added `include` to import list.
  - Imported `HealthCheckView` from `forecasting.api.views`.
  - Added `path('api/', include('forecasting.api.urls'))` to route API endpoints.
  - Set the home route to `HealthCheckView.as_view()`.

Exact file changed:
- `backend/config/urls.py` (updated imports and urlpatterns)

Why this fix is correct:
- Keeps API views organized under `forecasting.api`.
- Centralizes API routing under `/api/` which is consistent with project
  architecture and `forecasting/api/urls.py`.

---

## Root cause 2 — Admin template crash (runtime compatibility)

Symptoms:
- 500 errors when trying to open admin "add" pages (e.g. `/admin/auth/user/add/`).
- Tracebacks showed errors from Django internals while copying template context
  objects: `AttributeError: 'super' object has no attribute 'dicts'` in
  `django.template.context` copy logic.

Why it happened:
- The error originated in Django's `BaseContext.__copy__` implementation when it
  used `super().__copy__()` or `copy(super())` behavior that is incompatible
  with the active Python/Django runtime in this environment.
- This is a runtime compatibility issue (Django internals vs. Python version
  copying semantics) rather than an application-level bug.

Files added / changed to mitigate the issue:
- `backend/config/compat.py` (NEW)
  - Contains a small compatibility shim that patches `BaseContext.__copy__` and
    `Context.__copy__` to perform a safe copy of context attributes. The shim is
    minimal and targeted to address the copy behavior causing the admin crash.

- `backend/config/__init__.py` (edited)
  - Explicitly calls `patch_django_template_context_copy()` during Django
    startup so the shim is applied before templates/admin are used.

- `backend/forecasting/tests/test_admin_compat.py` (NEW)
  - Regression test to ensure `copy.copy(Context(...))` works and a few admin
    "add" pages render (status 200). This test prevents regressions in future.

Why a shim and not direct patch to Django:
- The underlying problem is an incompatibility between the installed Python and
  Django versions. Changing Django internals is not appropriate inside the
  site-packages. The shim ensures the project continues to work in this
  environment until you align runtime versions (preferred long-term fix).

Important: this is a pragmatic, local workaround. Recommended long-term
actions are listed below.

---

## Files changed / added (summary)

- Modified:
  - `backend/config/urls.py` — fix import path and add `include('forecasting.api.urls')`.
  - `backend/forecasting/api/views.py` — removed malformed nested `home()` method
    (it was inside `HealthCheckView` and used undefined `JsonResponse`). The
    `HealthCheckView.get()` method remains and serves as the root health endpoint.

- Added:
  - `backend/config/compat.py` — compatibility shim to patch Django context copy behavior.
  - `backend/config/__init__.py` — now imports and calls the patch function on startup.
  - `backend/forecasting/tests/test_admin_compat.py` — regression test for admin pages.
  - `ROOT_CAUSES_AND_FIXES.md` — (this file) human-readable summary.
  - `FIXES_APPLIED.md` — earlier created summary (kept in repo).

---

## Tests & verification performed

1. `python manage.py check` — passes with "System check identified no issues".
2. Imported and loaded URL patterns successfully with Django configured.
3. Verified the development server can be started and serves:
   - `/` (root)
   - `/admin/` and admin add pages for users/groups/models
4. Added and ran a regression test (new test file) to check admin add pages and
   context copy behavior.

Commands used for verification (copyable):

```powershell
cd backend
python manage.py check
python manage.py runserver
python manage.py test forecasting.tests.test_admin_compat
```

Note: When running tests or invoking Django from scripts, ensure
`DJANGO_SETTINGS_MODULE=config.settings` is set (manage.py sets that automatically).

---

## Recommended long-term actions (cleanup & prevent recurrence)

1. Align runtime versions: prefer using a known-compatible pair of Python and
   Django. For example, use Python 3.11 or 3.12 with Django 5.0.x (or upgrade
   Django to a version tested with Python 3.14).

2. Remove the compatibility shim once you upgrade to a Django release that
   includes an official fix (or after aligning Python/Django versions). Keep
   the regression test so the admin rendering remains tested.

3. Consider consolidating public views to a top-level `views.py` if you want a
   flat import surface. However, keeping API views inside `forecasting/api/`
   is perfectly valid and more modular for larger projects.

4. Add CI test(s) that run the `forecasting.tests.test_admin_compat` test on PRs
   to catch regressions early.

---

## Quick reference: exact code edits you may want to review

- `backend/config/urls.py` — now imports `include` and `HealthCheckView`:

```py
from django.contrib import admin
from django.urls import path, include
from forecasting.api.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('forecasting.api.urls')),
    path('', HealthCheckView.as_view(), name='home'),
]
```

- `backend/config/compat.py` — contains `patch_django_template_context_copy()`
  which patches `BaseContext.__copy__` and `Context.__copy__` to avoid the
  `dicts` copy problem.

- `backend/config/__init__.py` — calls `patch_django_template_context_copy()` at
  import time so the patch runs during Django startup.

- `backend/forecasting/api/views.py` — removed a misplaced `home()` function
  nested in the `HealthCheckView` class and unused `JsonResponse` import.

- `backend/forecasting/tests/test_admin_compat.py` — tests that admin add pages
  render successfully and that copying template Context works.

---

## Final notes

- The fixes are minimal and focused: they change routing and apply a controlled
  compatibility shim (no changes to third-party packages in site-packages).
- The shim is temporary and documented here — follow the recommended long-term
  actions to remove it.

If you want, I can:
- Add a one-line comment inside `config/compat.py` that explains why the shim
  exists and when it can be removed (i.e., specific Django/Python versions).
- Open a short PR description with the diffs and the rationale to commit to
  your repository. 

Which of those would you like me to do next?
