from django.contrib import admin
from django.urls import path
from medications.views import MedicineDashboardAPI, ContainerStatusAPI, MockIntakeAPI, PillHistoryAPI, RegisterTokenAPI
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/dashboard/', MedicineDashboardAPI.as_view(), name='dashboard'),
    path('api/history/', PillHistoryAPI.as_view(), name='pill-history'),
    path('api/status/', ContainerStatusAPI.as_view(), name='status'),
    path('api/test-intake/', MockIntakeAPI.as_view(), name='test-intake'),
    path('register-token/', RegisterTokenAPI.as_view(), name='register-token'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
