"""
Global DRF exception handler and ApiError class.
Ensures 100% adherence to Express errorMiddleware.js response structure.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated, PermissionDenied
from django.http import Http404

class ApiError(Exception):
    def __init__(self, error_dict=None, custom_message=None, status_code=None, errors=None):
        if error_dict:
            self.status_code = status_code or error_dict.get('statusCode', 400)
            self.message = custom_message or error_dict.get('message', 'Bad Request')
        else:
            self.status_code = status_code or 400
            self.message = custom_message or 'Bad Request'
        self.errors = errors or []
        super().__init__(self.message)

def custom_exception_handler(exc, context):
    # Handle ApiError explicitly
    if isinstance(exc, ApiError):
        return Response(
            {
                'success': False,
                'message': exc.message,
                'data': None,
                'meta': {},
                'errors': exc.errors,
            },
            status=exc.status_code,
        )

    # Let DRF handle standard exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        errors = []
        message = 'An error occurred.'

        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            msg = 'Unauthorized'
            if hasattr(exc, 'detail'):
                if isinstance(exc.detail, dict) and 'message' in exc.detail:
                    msg = exc.detail['message']
                else:
                    msg = str(exc.detail)
            return Response(
                {
                    'success': False,
                    'message': msg,
                    'data': None,
                    'meta': {},
                    'errors': [],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if isinstance(exc, ValidationError):
            message = 'Validation failed.'
            if isinstance(response.data, dict):
                for k, v in response.data.items():
                    msg = v[0] if isinstance(v, list) and len(v) > 0 else str(v)
                    errors.append({'path': k, 'message': msg})
            elif isinstance(response.data, list):
                for item in response.data:
                    errors.append({'path': 'non_field_errors', 'message': str(item)})
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            if isinstance(response.data, dict) and 'message' in response.data:
                message = response.data['message']
            else:
                message = 'Unauthorized'
        elif isinstance(exc, PermissionDenied):
            message = 'Forbidden'
        elif isinstance(exc, Http404):
            message = 'Not Found'
        else:
            if isinstance(response.data, dict):
                message = response.data.get('detail', str(response.data))
            else:
                message = str(response.data)

        return Response(
            {
                'success': False,
                'message': message,
                'data': None,
                'meta': {},
                'errors': errors,
            },
            status=response.status_code,
        )

    # Fallback for unexpected unhandled errors
    return Response(
        {
            'success': False,
            'message': 'Internal Server Error',
            'data': None,
            'meta': {},
            'errors': [str(exc)],
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
