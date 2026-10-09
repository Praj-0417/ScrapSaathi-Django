from django.urls import re_path
from collector.views import (
    AvailablePickupsView,
    CollectorPickupsView,
    AcceptPickupView,
    ReleasePickupView,
    CompletePickupView,
    PushCollectorLocationView,
)

urlpatterns = [
    re_path(r'^pickups/available/?$', AvailablePickupsView.as_view(), name='collector-available'),
    re_path(r'^pickups/?$', CollectorPickupsView.as_view(), name='collector-pickups'),
    re_path(r'^pickups/(?P<id>\d+)/accept/?$', AcceptPickupView.as_view(), name='collector-accept'),
    re_path(r'^pickups/(?P<id>\d+)/cancel/?$', ReleasePickupView.as_view(), name='collector-release'),
    re_path(r'^pickups/(?P<id>\d+)/complete/?$', CompletePickupView.as_view(), name='collector-complete'),
    re_path(r'^pickups/(?P<id>\d+)/location/?$', PushCollectorLocationView.as_view(), name='collector-location'),
]
