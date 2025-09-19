# chats/middleware.py

import logging
from datetime import datetime, time
from collections import defaultdict
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import re

# Configure logging for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler if it doesn't exist
if not logger.handlers:
    handler = logging.FileHandler('requests.log')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to a file, including timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user information
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Continue with the request
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging app during certain hours of the day.
    Access is only allowed between 6 AM and 9 PM.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current time
        current_time = timezone.now().time()
        
        # Define allowed time window (6 AM to 9 PM)
        start_time = time(6, 0)  # 6:00 AM
        end_time = time(21, 0)   # 9:00 PM
        
        # Check if current time is outside allowed window
        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden(
                "Access to the chat is restricted. Please try again between 6 AM and 9 PM."
            )
        
        # Continue with the request if within allowed time
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Middleware that implements rate limiting for chat messages based on IP address.
    Limits users to 5 messages per minute.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store message counts per IP
        self.message_counts = defaultdict(list)
        self.max_messages = 5  # Maximum messages per minute
        self.time_window = 60  # Time window in seconds (1 minute)

    def __call__(self, request):
        # Only apply rate limiting to POST requests (sending messages)
        if request.method == 'POST' and '/messages/' in request.path:
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = timezone.now().timestamp()
            
            # Clean up old entries (older than time window)
            self.message_counts[ip_address] = [
                timestamp for timestamp in self.message_counts[ip_address]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if user has exceeded the limit
            if len(self.message_counts[ip_address]) >= self.max_messages:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded. You can only send 5 messages per minute.',
                        'retry_after': self.time_window
                    },
                    status=429
                )
            
            # Add current request timestamp
            self.message_counts[ip_address].append(current_time)
        
        # Continue with the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware:
    """
    Middleware that checks user roles before allowing access to specific actions.
    Only admin and moderator users can perform certain actions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected paths that require admin/moderator access
        self.protected_paths = [
            '/admin/',
            '/messages/delete/',
            '/users/ban/',
            '/moderate/',
        ]

    def __call__(self, request):
        # Check if the request path requires special permissions
        if self.requires_elevated_permissions(request.path):
            # Check if user is authenticated
            if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
                return HttpResponseForbidden("Authentication required.")
            
            # Check user role
            user_role = getattr(request.user, 'role', None)
            if not user_role or user_role not in ['admin', 'moderator']:
                return HttpResponseForbidden(
                    "Access denied. Admin or moderator role required."
                )
        
        # Continue with the request
        response = self.get_response(request)
        return response
    
    def requires_elevated_permissions(self, path):
        """Check if the given path requires admin/moderator permissions."""
        return any(protected_path in path for protected_path in self.protected_paths)


# Additional middleware for detecting and blocking offensive language in messages
class OffensiveLanguageDetectionMiddleware:
    """
    Middleware that detects and blocks messages containing offensive language.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # List of offensive words (this should be more comprehensive in production)
        self.offensive_words = [
            'spam', 'hate', 'offensive', 'inappropriate',
            # Add more words as needed
        ]
    
    def __call__(self, request):
        # Check POST requests that might contain message content
        if request.method == 'POST' and '/messages/' in request.path:
            try:
                # Check if request has content to analyze
                if hasattr(request, 'body') and request.body:
                    import json
                    try:
                        data = json.loads(request.body)
                        message_content = data.get('content', '').lower()
                        
                        # Check for offensive language
                        if self.contains_offensive_language(message_content):
                            return JsonResponse(
                                {'error': 'Message contains inappropriate content and has been blocked.'},
                                status=400
                            )
                    except (json.JSONDecodeError, AttributeError):
                        # If we can't parse the body, continue normally
                        pass
            except Exception:
                # If anything goes wrong with content checking, continue normally
                pass
        
        response = self.get_response(request)
        return response
    
    def contains_offensive_language(self, text):
        """Check if text contains offensive language."""
        words = re.findall(r'\b\w+\b', text.lower())
        return any(word in self.offensive_words for word in words)