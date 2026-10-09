"""
Contact Inquiries Relational Model.
"""

from django.db import models

class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    subject = models.CharField(max_length=200, blank=True, default='General Inquiry')
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'contact_inquiries'
        ordering = ['-created_at']

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
