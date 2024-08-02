from rest_framework import serializers
from .models import *

class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserSerializers(serializers.ModelSerializer):
    task_set = TaskSerializers(many=True)
    class Meta:
        model = User
        fields =  ['username', 'first_name', 'last_name', 'task_set']