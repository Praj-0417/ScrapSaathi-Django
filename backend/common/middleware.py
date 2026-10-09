"""
Middleware for Request Context, Structured Request Logging, and Security Headers.
Preserves monolith observability behavior (requestId, durationMs, status).
"""

import time
import uuid
import logging
import threading

logger = logging.getLogger('scrapsaathi')
_thread_locals = threading.local()

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(_thread_locals, 'request_id', '-')
        return True

class RequestContextMiddleware:
    """
    Attaches unique request ID and logs requests with durationMs and status code.
    Matches Express app.js logging and context middleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-Id', str(uuid.uuid4()))
        request.request_id = request_id
        _thread_locals.request_id = request_id

        start_time = time.time()
        response = self.get_response(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Set security & tracking headers
        response['X-Request-Id'] = request_id
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'

        logger.info(
            'HTTP request: %s %s -> %s (%sms)',
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
            extra={'request_id': request_id},
        )

        return response
