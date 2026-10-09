"""
Pickup Request Relational Models.
Models scrap bookings with quote snapshots, status audit logs, and live tracking telemetry.
"""

from django.db import models
from common.constants import PICKUP_STATUS
from users.models import User

class PickupRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pickups', db_index=True)
    waste_collector = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_pickups', db_index=True
    )
    waste_details = models.JSONField(default=list)
    quote = models.JSONField(default=dict, blank=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    image_public_id = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    preferred_time_slot = models.CharField(max_length=100)
    customer_notes = models.TextField(blank=True, default='')
    collector_notes = models.TextField(blank=True, default='')
    settlement = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=30, default=PICKUP_STATUS.PENDING, choices=[(s, s) for s in PICKUP_STATUS.ALL], db_index=True
    )
    status_history = models.JSONField(default=list, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    live_tracking = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pickup_requests'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['waste_collector', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
        ordering = ['-created_at']

    def to_dict(self):
        """Produces serialized representation exactly matching Express Mongoose PickupRequest."""
        user_info = None
        if self.user:
            profile_addr = ''
            if hasattr(self.user, 'individual_profile') and self.user.individual_profile:
                profile_addr = self.user.individual_profile.address
            user_info = {
                '_id': str(self.user.id),
                'id': str(self.user.id),
                'name': self.user.name,
                'email': self.user.email,
                'phone': self.user.phone,
                'address': profile_addr or self.address,
            }

        collector_info = None
        if self.waste_collector:
            collector_info = {
                '_id': str(self.waste_collector.id),
                'id': str(self.waste_collector.id),
                'name': self.waste_collector.name,
                'email': self.waste_collector.email,
                'phone': self.waste_collector.phone,
            }

        location = None
        if self.latitude is not None and self.longitude is not None:
            location = {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude],
            }

        waste_details = self.waste_details or []
        waste_type = ', '.join(w.get('wasteType', '') for w in waste_details if w.get('wasteType'))
        quantity = sum(float(w.get('quantity', 0)) for w in waste_details)
        unit = waste_details[0].get('unit', 'kg') if waste_details else 'kg'
        subcategory = ', '.join(
            f"{w.get('subcategory') or w.get('wasteType', '')} ({w.get('quantity', '')} {w.get('unit', 'kg')})"
            for w in waste_details
        )

        return {
            '_id': str(self.id),
            'id': str(self.id),
            'userId': user_info,
            'wasteCollector': collector_info,
            'wasteDetails': waste_details,
            'wasteType': waste_type,
            'quantity': quantity,
            'unit': unit,
            'subcategory': subcategory,
            'quote': self.quote,
            'imageUrl': self.image_url,
            'imagePublicId': self.image_public_id,
            'address': self.address,
            'scheduledDate': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'preferredTimeSlot': self.preferred_time_slot,
            'customerNotes': self.customer_notes,
            'collectorNotes': self.collector_notes,
            'settlement': self.settlement,
            'status': self.status,
            'statusHistory': self.status_history,
            'location': location,
            'liveTracking': self.live_tracking,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
