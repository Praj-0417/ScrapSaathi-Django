from django.urls import re_path
from rates.views import RatesListView, RateItemUpdateView, RateItemCreateView, RateItemDeleteView

urlpatterns = [
    re_path(r'^/?$', RatesListView.as_view(), name='rates-list'),
    re_path(r'^/item/?$', RateItemUpdateView.as_view(), name='rates-item-update'),
    re_path(r'^/item/add/?$', RateItemCreateView.as_view(), name='rates-item-create'),
    re_path(r'^/item/(?P<item_id>[^/]+)/?$', RateItemDeleteView.as_view(), name='rates-item-delete'),
]
