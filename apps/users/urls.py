from django.urls import path

from rest_api.api import FriendRequestView, SearchUsersView, UserLoginView, UserSignupView
# from .views import FriendRequestCreateView, FriendRequestListView, FriendListView

urlpatterns = [
    # Users Signup
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    
    # Users Login
    path('login/', UserLoginView.as_view(), name='user-login'),

    # Search Users
    path('search-user/', SearchUsersView.as_view(), name='search-user'),

    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friend-request/<int:request_id>/', FriendRequestView.as_view(), name='manage-friend-request'),
    # Other paths...
]
