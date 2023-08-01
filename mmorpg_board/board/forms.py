from django import forms
from .models import Newsletter, Category, Advertisement
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['subject', 'content']


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'content', 'category', 'file']


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ResponseForm(forms.Form):
    content = forms.CharField(label='Отклик', widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите ваш отклик здесь...'}))