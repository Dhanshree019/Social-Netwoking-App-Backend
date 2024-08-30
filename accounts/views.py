from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import auth

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.helpers import *
from accounts.models import *
from accounts.serializers import *


# Create new user 

class SignupView(APIView):

    permission_classes = []
    authentication_classes = []

    @transaction.atomic
    def post(self, request):

        try:
            rd = request.data
            print("rd :", rd)

            if not User.objects.filter(email=rd['email'].lower()).exists():

                if is_valid_email(rd['email']):
                    user = User.objects.create_user(email=rd['email'].lower(), password=rd['password'], username=rd['email'], 
                                                    first_name=rd['first_name'], last_name=rd['last_name'])

                    data = UserSerializer(user).data
                    token = RefreshToken.for_user(user)

                    return Response({"success": True, "message": "Signup completed successfully !",
                                "data": data,
                                "authToken": {
                                    'type': 'Bearer',
                                    'access': str(token.access_token),
                                    'refresh': str(token),
                                }}, status=status.HTTP_201_CREATED)

                else:
                    return Response({"success": False, "message": "Invalid email format!"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": False, "message": "User already exists!"}, status=status.HTTP_409_CONFLICT)
        
        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Login existing user

class LoginView(APIView):

    permission_classes = []
    authentication_classes = []

    @transaction.atomic
    def post(self, request):

        try:
            rd = request.data
            print("rd :", rd)

            user = auth.authenticate(username=rd['email'], password=rd['password'])
            print("user :", user)

            if user:
                data = UserSerializer(user).data
                token = RefreshToken.for_user(user)

                return Response({"success": True, "message": "Login successful !",
                                "data": data,
                                "authToken": {
                                    'type': 'Bearer',
                                    'access': str(token.access_token),
                                    'refresh': str(token),
                                }}, status=status.HTTP_200_OK)

            return Response({"success": False, "message": "Credentials do not match!"}, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Search any user 

class SearchUserView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:
            keyword = request.GET.get('keyword', None)
            page = request.GET.get('page', 1)

            user = User.objects.filter(email=keyword).first()
            data = None

            if user:
                data = UserSerializer(user).data
            else:
                queryset = User.objects.filter((Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword)), is_superuser=False).exclude(id=request.user.id)
                paginated_queryset = paginate_queryset(queryset=queryset, page=page)
                data = UserSerializer(paginated_queryset, many=True).data

            return Response({"success": True, "message": "User searched!", "data": data}, status=status.HTTP_200_OK)

        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Send or accept friend request

class FriendRequestView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def post(self, request, action):
        try:
            rd = request.data
            print("rd :", rd)

            if action == "send":
                sender = User.objects.filter(id=request.user.id).first()
                receiver = User.objects.filter(id=rd['receiver']).first()
                if receiver:
                    if (not FriendRequest.objects.filter(sender=sender, receiver=receiver).exists()) and (request.user.id != receiver.id):

                        if check_friend_request_limit(request.user.id):
                            FriendRequest.objects.create(sender=sender, receiver=receiver)
                            return Response({"success": True, "message": "Friend request sent!"}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"success": False, "message": "You have reached friend requests limit for a minute!"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                    else:
                        return Response({"success": False, "message": "You are already friends!"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"success": False, "message": "Friend does not exist!"}, status=status.HTTP_404_NOT_FOUND)


            elif action == "accept":
                friend_request = FriendRequest.objects.filter(receiver__id=request.user.id, id=rd['friend_request_id']).first()
                print("friend request:",friend_request)
                if friend_request == None:
                    return Response({"success": False, "message": "Friend request not found!"}, status=status.HTTP_404_NOT_FOUND)

                friend_request.is_accepted = True
                friend_request.save()
                return Response({"success": True, "message": "Friend request accepted!"}, status=status.HTTP_200_OK)

            elif action == "reject":
                friend_request = FriendRequest.objects.filter(receiver__id=request.user.id, id=rd['friend_request_id'], is_accepted=False).first()
                if friend_request == None:
                    return Response({"success": False, "message": "Friend request not found!"}, status=status.HTTP_404_NOT_FOUND)

                friend_request.delete()
                return Response({"success": True, "message": "Friend request rejected!"}, status=status.HTTP_200_OK)

            else:
                return Response({"success": False, "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Show list of friends

class FriendsListView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:
            friends = FriendRequest.objects.filter(sender=request.user, is_accepted=True).values_list('receiver__id', flat=True)
            user = User.objects.filter(id__in=friends)
            data = UserSerializer(user, many=True).data

            return Response({"success": True, "message": "Friends list fetched!", "data": data}, status=status.HTTP_200_OK)
        
        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Show list of pending friend request 

class PendingFriendRequestView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):
        try:
            friend_requests = FriendRequest.objects.filter(receiver=request.user, is_accepted=False)
            data = PendingFriendRequestSerializer(friend_requests, many=True).data

            return Response({"success": True, "message": "Pending friend request fetched!", "data": data}, status=status.HTTP_200_OK)
        
        except Exception as err:
            print("Error :",err)
            return Response({"success":False,"message":"Unexpected error occurred!"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




