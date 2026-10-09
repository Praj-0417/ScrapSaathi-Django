"""
Contact View: Ingest and store customer support / contact inquiry.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from common.utils import api_success, api_failure
from contact.models import ContactInquiry

class ContactCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip() or 'General Inquiry'
        message = request.data.get('message', '').strip()

        if not name or not email or not message:
            return api_failure(message='Name, email, and message are required', status_code=400)

        inquiry = ContactInquiry.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        return api_success(
            data={'contactId': str(inquiry.id)},
            message='Your message has been received! Our green team will get back to you shortly.',
        )
