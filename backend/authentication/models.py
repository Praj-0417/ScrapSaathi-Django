"""
Authentication Models: OTP challenge storage.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    email = models.EmailField(db_index=True)
    otp = models.CharField(max_length=128)  # hashed or plain code
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_otps'
        ordering = ['-created_at']

    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()
