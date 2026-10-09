"""
Donations Relational Models.
Models donations, provisional receipts, and payment reconciliation states (Caveats #11 + #12).
"""

from django.db import models
from users.models import User

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', db_index=True)
    amount = models.FloatField()
    cause = models.CharField(max_length=50, default='general')
    donor_name = models.CharField(max_length=120, blank=True, default='')
    pan_number = models.CharField(max_length=15, blank=True, default='')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    payment_method = models.CharField(max_length=50, default='upi_qr')
    payment_status = models.CharField(max_length=30, default='pending')  # pending, completed, verified, failed
    verification_status = models.CharField(max_length=30, default='unverified')  # unverified, reconciled, failed
    receipt_type = models.CharField(max_length=50, default='provisional_acknowledgement')
    certificate_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    legal_disclaimer = models.TextField(
        default='Provisional acknowledgement issued upon UPI intent. Official 80G tax exemption certificates are issued only after payment reconciliation.'
    )
    message = models.TextField(blank=True, default='')
    reconciled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations'
        ordering = ['-created_at']

    def to_dict(self):
        user_info = None
        if self.user:
            user_info = {
                '_id': str(self.user.id),
                'id': str(self.user.id),
                'name': self.user.name,
                'email': self.user.email,
            }

        return {
            '_id': str(self.id),
            'id': str(self.id),
            'userId': user_info,
            'amount': self.amount,
            'cause': self.cause,
            'donorName': self.donor_name,
            'panNumber': self.pan_number,
            'transactionId': self.transaction_id,
            'paymentMethod': self.payment_method,
            'paymentStatus': self.payment_status,
            'verificationStatus': self.verification_status,
            'receiptType': self.receipt_type,
            'certificateId': self.certificate_id,
            'legalDisclaimer': self.legal_disclaimer,
            'message': self.message,
            'reconciledAt': self.reconciled_at.isoformat() if self.reconciled_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
