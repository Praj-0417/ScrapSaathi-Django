from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from authentication.models import OTP
from authentication.views import sign_verification_token

class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_requires_otp_challenge(self):
        payload = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'phone': '9876543210',
            'password': 'SecurePassword123!',
            'termsAccepted': True,
        }
        response = self.client.post('/api/v1/auth/register', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('Email must be verified', response.json()['message'])

    def test_full_otp_and_registration_flow(self):
        email = 'newuser@example.com'
        # 1. Send OTP
        res_send = self.client.post('/api/v1/auth/otp/send-registration', {'email': email}, format='json')
        self.assertEqual(res_send.status_code, 200)

        otp_record = OTP.objects.filter(email=email).first()
        self.assertIsNotNone(otp_record)

        # 2. Verify OTP with purpose=registration
        # Inject known plaintext OTP for test check
        otp_record.otp = '123456'
        otp_record.save()

        res_verify = self.client.post('/api/v1/auth/otp/verify?purpose=registration', {'email': email, 'otp': '123456'}, format='json')
        self.assertEqual(res_verify.status_code, 200)
        token = res_verify.json()['data']['verificationToken']
        self.assertTrue(token)

        # 3. Register
        reg_payload = {
            'name': 'New Verified User',
            'email': email,
            'phone': '9876543210',
            'password': 'SecurePassword123!',
            'termsAccepted': True,
            'verificationToken': token,
            'userType': 'individual',
            'address': 'Flat 101, Test Tower',
        }
        res_reg = self.client.post('/api/v1/auth/register', reg_payload, format='json')
        self.assertEqual(res_reg.status_code, 201)
        data = res_reg.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['email'], email)
        self.assertTrue('token' in data['data'])

        # 4. Check profile via /users/me
        jwt_token = data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token}')
        res_me = self.client.get('/api/v1/users/me')
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()['data']['user']['name'], 'New Verified User')

    def test_token_revocation_on_logout(self):
        user = User.objects.create_user(
            email='revoketest@example.com',
            password='TestPassword123!',
            name='Revoke Test',
        )
        login_res = self.client.post('/api/v1/auth/login', {'email': user.email, 'password': 'TestPassword123!'}, format='json')
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()['data']['token']

        # Request succeeds before logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res1 = self.client.get('/api/v1/users/me')
        self.assertEqual(res1.status_code, 200)

        # Logout
        res_logout = self.client.post('/api/v1/auth/logout')
        self.assertEqual(res_logout.status_code, 200)

        # Request fails after logout because tokenVersion incremented
        res2 = self.client.get('/api/v1/users/me')
        self.assertEqual(res2.status_code, 401)
        self.assertIn('Session has been revoked', res2.json()['message'])
