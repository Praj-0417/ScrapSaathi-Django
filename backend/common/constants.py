"""
System-wide constants, HTTP message strings, error definitions, and operational constants.
Preserves exact text and codes from Express monolith.
"""

class MESSAGES:
    HEALTH_OK = 'ScrapSaathi backend is healthy'
    API_HEALTH_OK = 'ScrapSaathi API v1 is healthy'
    USER_REGISTERED = 'User registered successfully'
    LOGIN_SUCCESS = 'Logged in successfully'
    OTP_SENT = 'OTP sent successfully'
    OTP_VERIFIED = 'OTP verified successfully'
    PASSWORD_RESET_SUCCESS = 'Password has been reset successfully'
    PROFILE_UPDATED = 'Profile updated successfully'
    USER_FETCHED = 'User profile fetched successfully'
    PICKUP_CREATED = 'Pickup request created successfully'
    PICKUP_ACCEPTED = 'Pickup request accepted successfully'
    PICKUP_CANCELLED = 'Pickup request cancelled successfully'
    PICKUP_COMPLETED = 'Pickup request completed successfully'
    PICKUPS_FETCHED = 'Pickup requests retrieved successfully'
    DONATION_CREATED = 'Donation recorded successfully'
    DONATIONS_FETCHED = 'Donations retrieved successfully'
    ADMIN_LOGIN_SUCCESS = 'Admin logged in successfully'
    USERS_FETCHED = 'Users retrieved successfully'


class ERROR_CODES:
    INTERNAL_SERVER_ERROR = {'statusCode': 500, 'message': 'Internal Server Error'}
    NOT_FOUND = {'statusCode': 404, 'message': 'Not Found'}
    BAD_REQUEST = {'statusCode': 400, 'message': 'Bad Request'}
    UNAUTHORIZED = {'statusCode': 401, 'message': 'Unauthorized'}
    FORBIDDEN = {'statusCode': 403, 'message': 'Forbidden'}
    CONFLICT = {'statusCode': 409, 'message': 'Conflict'}
    TOO_MANY_REQUESTS = {'statusCode': 429, 'message': 'Too many requests, please try again later'}

    USER_ALREADY_EXISTS = {'statusCode': 400, 'message': 'User with this email already exists'}
    INVALID_CREDENTIALS = {'statusCode': 401, 'message': 'Invalid email or password'}
    TERMS_NOT_ACCEPTED = {'statusCode': 400, 'message': 'You must accept the Terms and Conditions to register'}
    USER_NOT_FOUND = {'statusCode': 404, 'message': 'User not found'}
    PROFILE_NOT_FOUND = {'statusCode': 404, 'message': 'Profile not found'}

    INVALID_OTP = {'statusCode': 400, 'message': 'Invalid OTP'}
    OTP_SEND_FAILED = {'statusCode': 500, 'message': 'Failed to send OTP'}
    OTP_EXPIRED = {'statusCode': 400, 'message': 'OTP has expired'}
    OTP_NOT_VERIFIED = {'statusCode': 400, 'message': 'Email must be verified with OTP before registration'}
    GOOGLE_AUTH_FAILED = {'statusCode': 401, 'message': 'Google authentication failed. Invalid or expired credential.'}
    TOKEN_REVOKED = {'statusCode': 401, 'message': 'Session has been revoked. Please log in again.'}

    PICKUP_NOT_FOUND = {'statusCode': 404, 'message': 'Pickup request not found'}
    PICKUP_ALREADY_ACCEPTED = {'statusCode': 409, 'message': 'This pickup request has already been accepted or does not exist.'}
    PICKUP_INVALID_CANCEL = {'statusCode': 400, 'message': 'Cannot cancel this pickup. It may not exist, not belong to you, or already be completed.'}
    PICKUP_INVALID_TRANSITION = {'statusCode': 409, 'message': 'Invalid state transition or concurrent modification detected.'}

    TRACKING_NOT_ALLOWED = {'statusCode': 403, 'message': 'You are not authorized to access tracking for this pickup.'}
    TRACKING_NOT_FOUND = {'statusCode': 404, 'message': 'No live tracking data found for this pickup.'}

    LOCATION_NOT_SERVICEABLE = {
        'statusCode': 400,
        'message': 'Selected location is outside our operational service area. ScrapSaathi currently operates in Delhi NCR, Mumbai, Bengaluru, Pune, Hyderabad, Jaipur, Lucknow, Kolkata, and Chennai.',
    }


class USER_TYPES:
    INDIVIDUAL = 'individual'
    WASTE_COLLECTOR = 'waste-collector'
    BIG_ORGANIZATION = 'big-organization'
    RECYCLE_COMPANY = 'recycle-company'
    ALL = [INDIVIDUAL, WASTE_COLLECTOR, BIG_ORGANIZATION, RECYCLE_COMPANY]


class ROLES:
    USER = 'user'
    ADMIN = 'admin'
    ALL = [USER, ADMIN]


class PICKUP_STATUS:
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ALL = [PENDING, ACCEPTED, COMPLETED, CANCELLED]


SERVICE_HUBS = [
    {'id': 'delhi-ncr', 'name': 'Delhi NCR', 'lat': 28.6139, 'lon': 77.2090, 'maxRadiusKm': 50},
    {'id': 'mumbai', 'name': 'Mumbai MMR', 'lat': 19.0760, 'lon': 72.8777, 'maxRadiusKm': 45},
    {'id': 'bengaluru', 'name': 'Bengaluru', 'lat': 12.9716, 'lon': 77.5946, 'maxRadiusKm': 40},
    {'id': 'pune', 'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567, 'maxRadiusKm': 35},
    {'id': 'hyderabad', 'name': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867, 'maxRadiusKm': 40},
    {'id': 'jaipur', 'name': 'Jaipur', 'lat': 26.9124, 'lon': 75.7873, 'maxRadiusKm': 30},
    {'id': 'lucknow', 'name': 'Lucknow', 'lat': 26.8467, 'lon': 80.9462, 'maxRadiusKm': 30},
    {'id': 'kolkata', 'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639, 'maxRadiusKm': 35},
    {'id': 'chennai', 'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707, 'maxRadiusKm': 35},
]
