from functools import wraps
from django.core.cache import cache
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


def rate_limit_friend_requests(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Check if the user is authenticated and has a user attribute
        user_id = getattr(request.user, 'id', None)
        if user_id is None:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check the cache for the number of friend requests sent by the user in the last minute
        cache_key = f"friend_requests_limit:{user_id}"
        request_count = cache.get(cache_key, 0)

        # Update the cache with the current timestamp
        cache.set(cache_key, request_count + 1, timeout=60)

        # Check if the user has sent more than 3 friend requests within the last minute
        if request_count >= 3:
            return Response({"error": "You have reached the friend request limit. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Call the original function
        return func(self, request, *args, **kwargs)

    return wrapper