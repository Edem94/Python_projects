from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Name')
    last_name = forms.CharField(max_length=30, required=False, help_text='Surname')
    date_of_birth = forms.DateField(required=True, help_text='Date of birth')
    city = forms.CharField(max_length=36, required=False, help_text='City')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("user", "city", "date_of_birth", "avatar",)

