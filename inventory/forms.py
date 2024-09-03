from django import forms
from django.contrib.auth.forms import UserCreationForm
from inventory.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
