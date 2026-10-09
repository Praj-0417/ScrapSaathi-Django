"""
Common Views: Health, Geocoding, and Serviceability.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from common.utils import api_success, api_failure, check_serviceability, find_local_localities, reverse_lookup_locality
from common.constants import MESSAGES

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return api_success(message=MESSAGES.HEALTH_OK)

class ApiV1HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return api_success(
            data={'service': 'scrapsaathi-api', 'version': 'v1'},
            message=MESSAGES.API_HEALTH_OK,
        )

class GeocodeSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = min(int(request.query_params.get('limit', 5)), 10)

        if not query:
            return api_success(data=[])

        local_results = find_local_localities(query, limit)
        return api_success(data=local_results, message='Geocoding results retrieved')

class GeocodeReverseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon') or request.query_params.get('lng')

        if not lat or not lon:
            return api_failure(message='Valid lat and lon query parameters are required', status_code=400)

        result = reverse_lookup_locality(lat, lon)
        if not result:
            return api_failure(message='Valid lat and lon query parameters are required', status_code=400)

        return api_success(data=result)

class GeocodeServiceabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon') or request.query_params.get('lng')

        if not lat or not lon:
            return api_failure(message='Valid lat and lon query parameters are required', status_code=400)

        result = check_serviceability(lat, lon)
        msg = (
            'Location is within active service coverage'
            if result.get('serviceable')
            else 'Location currently outside active service coverage'
        )
        return api_success(data=result, message=msg)
