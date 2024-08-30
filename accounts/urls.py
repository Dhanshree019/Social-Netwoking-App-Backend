from django.urls import path
from accounts.views import *

urlpatterns = [
    path('signup', SignupView.as_view(), name="signup"),
    path('login', LoginView.as_view(), name="login"),
    path('search', SearchUserView.as_view(), name="search-users"),
    path('friend-request/<str:action>', FriendRequestView.as_view(), name="friend-request-action"),
    path('friends', FriendsListView.as_view(), name="friends"),
    path('pending-request', PendingFriendRequestView.as_view(), name="pending-request"),
]


