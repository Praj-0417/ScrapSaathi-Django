from django.urls import re_path
from contact.views import ContactCreateView

urlpatterns = [
    re_path(r'^/?$', ContactCreateView.as_view(), name='contact-create'),
]
