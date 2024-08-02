from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_done = models.BooleanField(default=False)
    deadline = models.DateField()

    def __str__(self):
        username = self.user.username if self.user else 'Not set'
        return f'Task {self.name} was created by {self.creator} and will be executed by {self.executor} before {self.deadline}. STATUS {self.is_done}'