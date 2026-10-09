from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from rates.models import ScrapRateCategory, ScrapItem
from authentication.views import generate_jwt_token

class PickupsAndCollectorTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Seed test rate item
        cat = ScrapRateCategory.objects.create(
            category_id='paper', name='Paper', icon='📰', order=1, active=True
        )
        ScrapItem.objects.create(
            category=cat,
            item_id='newspaper',
            name='Newspaper (Raddi)',
            unit='kg',
            prices={'delhi-ncr': 15, 'bengaluru': 14},
            active=True,
        )

        # Create regular user
        self.user = User.objects.create_user(
            email='customer@example.com', password='Password123!', name='Test Customer'
        )
        self.user_token = generate_jwt_token(self.user)

        # Create collector 1
        self.collector1 = User.objects.create_user(
            email='collector1@example.com',
            password='Password123!',
            name='Collector Alpha',
            user_type='waste-collector',
        )
        self.c1_token = generate_jwt_token(self.collector1)

        # Create collector 2
        self.collector2 = User.objects.create_user(
            email='collector2@example.com',
            password='Password123!',
            name='Collector Beta',
            user_type='waste-collector',
        )
        self.c2_token = generate_jwt_token(self.collector2)

    def test_pickup_lifecycle_and_atomic_acceptance(self):
        # 1. Customer creates pickup with Delhi NCR coordinates
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        create_payload = {
            'address': 'Connaught Place, New Delhi',
            'preferredTimeSlot': '10:00 AM - 12:00 PM',
            'latitude': 28.6315,
            'longitude': 77.2167,
            'wasteDetails': [
                {'wasteType': 'Newspaper (Raddi)', 'quantity': 10, 'unit': 'kg'}
            ],
            'customerNotes': 'Call before arrival',
        }
        res_create = self.client.post('/api/v1/pickups', create_payload, format='json')
        self.assertEqual(res_create.status_code, 201)
        data_create = res_create.json()
        pickup_id = data_create['data']['pickup']['id']

        # Verify quote snapshot was calculated by backend
        quote = data_create['data']['pickup']['quote']
        self.assertEqual(quote['totalEstimate'], 150.0)
        self.assertEqual(quote['items'][0]['unitRate'], 15.0)

        # 2. Collector 1 lists available pickups
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.c1_token}')
        res_avail = self.client.get('/api/v1/collector/pickups/available?latitude=28.63&longitude=77.21&radius=15')
        self.assertEqual(res_avail.status_code, 200)
        self.assertTrue(any(p['id'] == str(pickup_id) for p in res_avail.json()['data']['pickups']))

        # 3. Collector 1 accepts pickup atomically
        res_accept1 = self.client.post(f'/api/v1/collector/pickups/{pickup_id}/accept')
        self.assertEqual(res_accept1.status_code, 200)
        self.assertEqual(res_accept1.json()['data']['pickup']['status'], 'accepted')

        # 4. Collector 2 attempts to accept the SAME pickup -> Must fail with 409 Conflict
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.c2_token}')
        res_accept2 = self.client.post(f'/api/v1/collector/pickups/{pickup_id}/accept')
        self.assertEqual(res_accept2.status_code, 409)
        self.assertIn('already been accepted', res_accept2.json()['message'])

        # 5. Collector 1 pushes live GPS coordinates
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.c1_token}')
        res_loc = self.client.post(
            f'/api/v1/collector/pickups/{pickup_id}/location',
            {'latitude': 28.632, 'longitude': 77.218, 'speed': 25, 'heading': 90},
            format='json',
        )
        self.assertEqual(res_loc.status_code, 200)

        # 6. Customer views tracking
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        res_track = self.client.get(f'/api/v1/pickups/{pickup_id}/tracking')
        self.assertEqual(res_track.status_code, 200)
        self.assertEqual(res_track.json()['data']['liveTracking']['speed'], 25)

        # 7. Collector 1 completes pickup with weighment & settlement
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.c1_token}')
        res_complete = self.client.post(
            f'/api/v1/collector/pickups/{pickup_id}/complete',
            {
                'finalWeight': 10.5,
                'settledAmount': 157.5,
                'collectorNotes': 'Weighed on digital scale',
            },
            format='json',
        )
        self.assertEqual(res_complete.status_code, 200)
        completed_data = res_complete.json()['data']['pickup']
        self.assertEqual(completed_data['status'], 'completed')
        self.assertEqual(completed_data['settlement']['finalWeight'], 10.5)
        self.assertEqual(completed_data['settlement']['settledAmount'], 157.5)
