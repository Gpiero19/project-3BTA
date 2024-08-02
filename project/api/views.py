from django.shortcuts import render
from .models import *
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import generics, views, status


# Create your views here.

class UserCreateView(APIView):

    def post(self, request):
        # Extract the data from the request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Check for missing fields
        if not username or not password or not email:
            return Response({'error': 'Username, password, and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Prepare the response data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        return Response(user_data, status=status.HTTP_201_CREATED)
    
class ClearDatabaseView(APIView):
    def post(self, request):
        Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)
    

class LoginView(views.APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'invalid credentials'}, status= status.HTTP_401_UNAUTHORIZED)