from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    executor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_done = models.BooleanField(default=False)
    deadline = models.DateField()