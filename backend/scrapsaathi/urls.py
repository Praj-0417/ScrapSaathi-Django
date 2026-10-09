"""
ScrapSaathi URL Configuration with full slash-optional regex matching.
Dual-mounts canonical /api/v1 and /api aliases.
"""

from django.contrib import admin
from django.urls import path, re_path, include
from common.views import HealthCheckView, ApiV1HealthView

api_v1_patterns = [
    re_path(r'^health/?$', ApiV1HealthView.as_view(), name='api-health'),
    re_path(r'^auth/', include('authentication.urls')),
    re_path(r'^otp/', include('authentication.urls')),
    re_path(r'^users/', include('users.urls')),
    re_path(r'^pickups', include('pickups.urls')),
    re_path(r'^collector/', include('collector.urls')),
    re_path(r'^rates', include('rates.urls')),
    re_path(r'^donations', include('donations.urls')),
    re_path(r'^contact', include('contact.urls')),
    re_path(r'^admin/', include('users.admin_urls')),
    re_path(r'^geocode/', include('common.geocode_urls')),
]

urlpatterns = [
    # Global health (no auth, no rate limiting)
    re_path(r'^health/?$', HealthCheckView.as_view(), name='root-health'),

    # Prometheus metrics exporter
    path('', include('django_prometheus.urls')),

    # Canonical and alias API routes
    re_path(r'^api/v1/', include((api_v1_patterns, 'api-v1'))),
    re_path(r'^api/', include((api_v1_patterns, 'api-canonical'))),

    # Django built-in admin dashboard
    path('django-admin/', admin.site.urls),
]
