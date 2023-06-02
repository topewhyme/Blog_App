from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


from django import forms
from .models import AuthorRequest, Blog

class AuthorRequestForm(forms.ModelForm):
    class Meta:
        model = AuthorRequest
        fields = ['first_name', 'last_name', 'bio']  
        
from django import forms

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name', 'description']