from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import CustomUser, FriendRequest
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import FriendRequestSerializer, UserListSerializer, UserSignupSerializer, UserLoginSerializer
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserSignupView(APIView):
    """
    API endpoint for user registration.

    Accepts POST requests with user registration data. If the provided data is valid,
    a new user is created, and a success message along with user data is returned.
    If the data is invalid, error details are returned.

    Request:
    - Method: POST
    - URL: /api/signup/

    Response:
    - 201 Created: User created successfully.
    - 400 Bad Request: Invalid data provided.
    """
    def post(self, request, *args, **kwargs):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            message = "User created successfully!"
            return Response({"message": message, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    """
    API endpoint for user login.

    Accepts POST requests with user login data. If the provided data is valid,
    a JWT token pair (access and refresh) is generated and returned.
    If the data is invalid, error details are returned.

    Request:
    - Method: POST
    - URL: /api/login/

    Response:
    - 200 OK: Login successful, returns JWT tokens.
    - 400 Bad Request: Invalid data provided.
    """
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error":"User not registered!please signup!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":"An error occured"},  status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the provided password matches the user's password
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class SearchUsersView(APIView):
    """
    API endpoint to search users by email and name.

    Accepts GET requests with a search keyword. The search is performed
    on both email and name, and results are paginated (up to 10 records per page).
    Only authenticated users with valid JWT tokens can access this endpoint.
    """
  
    def get(self, request, *args, **kwargs):
        search_keyword = request.query_params.get('q', '')

        # Perform the search on both email and name using Q objects
        users = CustomUser.objects.filter(
            Q(email__iexact=search_keyword) | Q(username__icontains=search_keyword)
        ).distinct()

        # Paginate the results (adjust page size as needed)
        page = request.query_params.get('page', 1)
        paginator = Paginator(users, 10)

        try:
            paginated_users = paginator.page(page)
        except EmptyPage:
            return Response({"error": "No more results"}, status=status.HTTP_204_NO_CONTENT)

        serializer = UserListSerializer(paginated_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class FriendRequestView(APIView):
    """
    API endpoint for sending/accepting/rejecting friend requests.

    This endpoint allows authenticated users with valid JWT tokens to perform
    actions related to friend requests.

    - To send a friend request, make a POST request to this endpoint with the
      target user's ID in the 'to_user' field.

    - To accept or reject a friend request, make a PATCH request to this endpoint
      with the friend request ID in the URL and the 'action' field set to 'accept'
      or 'reject'.

    Request Methods:
    - POST: Send a friend request
    - PATCH: Accept or reject a friend request

    Request Format:
    - POST Data:
        {
            "to_user": <target_user_id>
        }

    - PATCH Data:
        {
            "action": "accept" or "reject"
        }

    Response:
    - 201 Created: Friend request sent successfully
    - 200 OK: Friend request accepted or rejected successfully
    - 400 Bad Request: Invalid action or serializer errors
    - 401 Unauthorized: User is not authenticated or has invalid tokens
    - 404 Not Found: Friend request with the given ID not found
    """

    def post(self, request, *args, **kwargs):
        # Send friend request
        data = request.data
        print(data)
        data['from_user'] = request.user.id
        print(data)
        serializer = FriendRequestSerializer(data=data)
        if serializer.is_valid():
            to_user_id = data.get('to_user')
            to_user = get_object_or_404(CustomUser, id=to_user_id)
            serializer.save()
            return Response({"message":"friend request successfully requested","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def patch(self, request, request_id, *args, **kwargs):
        # Accept or reject friend request
        friendship_request = get_object_or_404(FriendRequest, id=request_id)
        action = request.data.get('action')

        if action == 'accept':
            friendship_request.accept
        elif action == 'reject':
            friendship_request.reject
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Friend request {action}ed successfully"}, status=status.HTTP_200_OK)

