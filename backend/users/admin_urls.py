from django.urls import re_path
from users.views import AdminUserListView
from authentication.views import AdminLoginView
from pickups.views import AdminPickupListView
from donations.views import AdminDonationListView

urlpatterns = [
    re_path(r'^auth/login/?$', AdminLoginView.as_view(), name='admin-login'),
    re_path(r'^users/?$', AdminUserListView.as_view(), name='admin-users'),
    re_path(r'^pickups/?$', AdminPickupListView.as_view(), name='admin-pickups'),
    re_path(r'^donations/?$', AdminDonationListView.as_view(), name='admin-donations'),
]
