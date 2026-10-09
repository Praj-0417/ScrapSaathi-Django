from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from authentication.views import generate_jwt_token

class RatesAndDonationsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='donor@example.com', password='Password123!', name='Eco Donor'
        )
        self.user_token = generate_jwt_token(self.user)

    def test_rates_board_by_city(self):
        res = self.client.get('/api/v1/rates?city=delhi-ncr')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['city'], 'delhi-ncr')
        self.assertTrue(len(data['data']['categories']) > 0)

    def test_donation_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        res = self.client.post(
            '/api/v1/donations',
            {
                'amount': 250,
                'cause': 'environment',
                'donorName': 'Green Hero',
                'transactionId': 'UPI-REF-998877',
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        donation = res.json()['data']['donation']
        self.assertEqual(donation['amount'], 250.0)
        self.assertTrue(donation['certificateId'].startswith('ACK-ECO-'))
        self.assertEqual(donation['paymentStatus'], 'completed')
