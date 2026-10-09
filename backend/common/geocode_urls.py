from django.urls import re_path
from common.views import GeocodeSearchView, GeocodeReverseView, GeocodeServiceabilityView

urlpatterns = [
    re_path(r'^search/?$', GeocodeSearchView.as_view(), name='geocode-search'),
    re_path(r'^reverse/?$', GeocodeReverseView.as_view(), name='geocode-reverse'),
    re_path(r'^serviceable/?$', GeocodeServiceabilityView.as_view(), name='geocode-serviceable'),
]
