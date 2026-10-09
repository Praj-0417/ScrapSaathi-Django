from django.test import TestCase
from rest_framework.test import APIClient

class HealthAndMetricsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_global_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'ScrapSaathi backend is healthy')

    def test_api_v1_health(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['service'], 'scrapsaathi-api')
        self.assertEqual(data['data']['version'], 'v1')

    def test_api_canonical_health_alias(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['service'], 'scrapsaathi-api')

    def test_prometheus_metrics_endpoint(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn('django_http_requests_before_middlewares_total', response.content.decode())
