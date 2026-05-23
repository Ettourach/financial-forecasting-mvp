from django.contrib import admin
from django.urls import path, include
from forecasting.api.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('forecasting.api.urls')),
    path('', HealthCheckView.as_view(), name='home'),
]

