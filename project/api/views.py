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

'''This view allows for the creation of a user.

1. Implement the `post` method to handle POST requests for creating a new user.
2. Check for the presence of: `username`, `password`, and `email`. If any of these values are missing in the request body, return an error message `{'error': 'Username, password, and email are required'}` with the status code `400 BAD REQUEST`.
3. Check if a user with the specified `username` already exists. If a user with this username already exists, return an error message `{'error': 'Username already exists'}` with the status code `400 BAD REQUEST`.
4. If all data is valid, create a new user. Upon successful creation of the user, return a user data (id, username, email) in JSON format with the status code `201 CREATED`.

Hint: To work with the `User` model and send HTTP responses, use the appropriate functions from Django REST Framework: `User.objects.create_user`, `Response`.'''

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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(creator=user)
    
'''This view allows displaying the tasks created by the current user.

1. Only authenticated users can use this view.
2. This view should return a complete description of all tasks created by the user in the form of a list.

Fields for each task: executor, name, cost, deadline.'''

class TaskWithExecutorAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
    
class UserTasksAPIView(generics.ListCreateAPIView): #check if all fields needed are shown
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(User=User)
    
class UserTasksStatsAPIView():
    pass

'''This view allows displaying statistics for the tasks of the current user.

1. Only authenticated users can use this view.
2. The `get` method should return the following statistics in JSON format:
   - Number of completed tasks (key: `completed_tasks`)
   - Number of pending tasks (key: `pending_tasks`)
   - Number of overdue tasks (key: `overdue_tasks`)
   - Number of tasks assigned to the user (key: `assigned_tasks`)
   - Total amount earned: The sum of the cost of all tasks completed by this user (key: `total_earned`)
   - Total amount spent: The sum of the cost of all tasks assigned by this user (key: `total_spent`)
3. The values for `total_earned` and `total_spent` should be 0 if there are no corresponding tasks (handle None values).
4. The response should be returned in JSON format with a status code of 200 OK.

Example result: `{'completed_tasks': 0, 'pending_tasks': 5, 'overdue_tasks': 0, 'assigned_tasks': 1, 'total_earned': 0, 'total_spent': 6000.0}`'''

class UnassignedTasksAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(executor=None).order_by('price') 
        #filtering where executor is none and sorted with ascending price
        #check if it shows all the fields requested Fields for each task: executor, name, cost, deadline.


class BecomeExecutorAPIView():
    pass

'''This view allows the user to become the executor of the task.

1. Only authenticated users can use this view.
2. The view should implement the `patch` method, which receives the task identifier through the URL.
3. If the task is not found, return an error message `{'error': 'Task not found'}` with the status code `404 Not Found`.
4. If the current user is the creator of the task, return an error message `{'error': 'You cannot assign yourself as executor of your own task'}` with the status code `400 Bad Request`.
5. If the task already has an executor, return an error message `{'error': 'This task already has an executor'}` with the status code `400 Bad Request`.
6. If the task is available for assignment, set the current user as the executor and save the task.
8. Return a successful response with the status code `200 OK` and the message `{'message': 'You have been assigned as the executor of the task'}`.'''

class MarkTaskDoneAPIView():
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        pass

    def get_queryset(self, request):
        data = request.data.copy()
        user = self.request.user
        if user != data['executor']:
            return Response(
                {'error': 'You are not authorized to mark this task as done'},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        

'''This view allows marking a task as done.

1. Only authenticated users can use this view.
2. The view implements the `patch` method, which receives the task identifier through the URL.
3. If the task is not found, it returns an error message `{'error': 'Task not found'}` with the status code `404 Not Found`.
4. If the current user is not the executor of the task, it returns an error message `{'error': 'You are not authorized to mark this task as done'}` with the status code `400 Bad Request`.
5. If all checks pass successfully, it sets the value of the `is_done` field to True for the current task and saves the changes.
6. It returns a successful response with the status code `200 OK`, passing the modified task data in JSON format as the response data.

Fields for the task: executor, name, cost, deadline. '''