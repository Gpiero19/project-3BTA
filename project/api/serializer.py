from rest_framework import serializers
from .models import *

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'creator', 'executor', 'cost', 'is_done', 'deadline']
        read_only_fields = ['creator', 'is_done', 'deadline']

class UserSerializers(serializers.ModelSerializer):
    task_set = TaskSerializer(many=True)
    class Meta:
        model = User
        fields =  ['username', 'first_name', 'last_name', 'task_set']

class CreateUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Create the user but do not save yet
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        # Set the password properly with hashing
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        # Validate the presence of required fields
        if not data.get('username'):
            raise serializers.ValidationError("Username is required")
        if not data.get('password'):
            raise serializers.ValidationError("Password is required")
        if not data.get('email'):
            raise serializers.ValidationError("Email is required")
        
        # Check if a user with the specified username already exists
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError("Username already exists")
        
        return data