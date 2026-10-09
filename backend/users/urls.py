from django.urls import re_path
from users.views import UserMeView, UserProfileView

urlpatterns = [
    re_path(r'^me/?$', UserMeView.as_view(), name='user-me'),
    re_path(r'^me/profile/?$', UserProfileView.as_view(), name='user-profile'),
]
