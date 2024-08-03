from django.shortcuts import render
from .models import *
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import generics, views, status
from .serializer import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .forms import * 
from django.views.generic import ListView


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializers

    def post(self, request, *args, **kwargs):
        # Check for presence of username, password, and email
        required_fields = ['username', 'password', 'email']     
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': 'Username, password, and email are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        # Check if a user with the specified username already exists
        if User.objects.filter(username=request.data.get('username')).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If all checks pass, proceed with serializer validation and user creation
        return super().post(request, *args, **kwargs)


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
    
class LogoutView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        data = {"message": "Successfully logged out"}
        return Response(data, status=status.HTTP_200_OK)
    
class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        
        # Specify the creator as the current authenticated user
        creator = request.user
        data['creator'] = creator.id

        if 'executor' in data and data['executor'] == str(creator.id):
            return Response(
                {'error': 'The creator of a task cannot be its executor'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the specified executor exists
        if 'executor' in data:
            executor_id = data['executor']
            if executor_id:
                try:
                    executor = User.objects.get(id=executor_id)
                except User.DoesNotExist:
                    data['executor'] = None

        # Serialize and validate the data
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TasksCreatedByUser(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(creator=user)

class TaskWithExecutorAPIView():
    pass