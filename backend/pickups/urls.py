from django.urls import re_path
from pickups.views import (
    PickupListCreateView,
    PickupDetailView,
    PickupCancelView,
    PickupTrackingView,
)

urlpatterns = [
    re_path(r'^/?$', PickupListCreateView.as_view(), name='pickup-list-create'),
    re_path(r'^/(?P<id>\d+)/?$', PickupDetailView.as_view(), name='pickup-detail'),
    re_path(r'^/(?P<id>\d+)/cancel/?$', PickupCancelView.as_view(), name='pickup-cancel'),
    re_path(r'^/(?P<id>\d+)/tracking/?$', PickupTrackingView.as_view(), name='pickup-tracking'),
]
