# from django import forms
# from .models import *
# from django.contrib.auth.models import User
# from django.contrib.auth.hashers import make_password

# class TaskForm(forms.ModelForm):
#     name = forms.CharField(max_length=255)
#     cost = forms.DecimalField(max_digits=8, decimal_places=2)
#     is_done = forms.BooleanField(default=False)
#     deadline = forms.DateField()

#     class Meta:
#         model = Task
#         fields = ['username', 'email', 'name', 'is_done', 'deadline']
    
#     def save(self):
#         task = User.objects.create(
#             username = self.cleaned_data['username'],
#             email = self.cleaned_data['email'],
#             password = make_password(self.cleaned_data['password']),
#         )

#         teacher = Task.objects.create(
#             task = task,
#             subject = self.cleaned_data['subject'],
#         )

#         return teacher