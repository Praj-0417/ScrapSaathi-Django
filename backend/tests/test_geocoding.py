from django.test import TestCase
from rest_framework.test import APIClient

class GeocodingAndServiceabilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_serviceable_location_delhi(self):
        # Connaught Place, Delhi (28.6315, 77.2167)
        res = self.client.get('/api/v1/geocode/serviceable?lat=28.6315&lon=77.2167')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['data']['serviceable'])
        self.assertEqual(data['data']['hubId'], 'delhi-ncr')

    def test_unserviceable_location(self):
        # Leh, Ladakh coordinates (34.1526, 77.5771) -> outside service radius
        res = self.client.get('/api/v1/geocode/serviceable?lat=34.1526&lon=77.5771')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data['data']['serviceable'])

    def test_geocode_search(self):
        res = self.client.get('/api/v1/geocode/search?q=Connaught')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data['data']) > 0)
        self.assertIn('Connaught Place', data['data'][0]['display_name'])
