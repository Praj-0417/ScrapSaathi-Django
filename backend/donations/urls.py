from django.urls import re_path
from donations.views import DonationCreateView, MyDonationsView

urlpatterns = [
    re_path(r'^/?$', DonationCreateView.as_view(), name='donation-create'),
    re_path(r'^/me/?$', MyDonationsView.as_view(), name='donation-me'),
]
