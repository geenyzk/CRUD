from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, PasswordInput, EmailInput

# Register form
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password1': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        }

# Login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class AdminCreateUserForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    is_staff = forms.BooleanField(required=False, label='Admin (can access staff area)')
    is_superuser = forms.BooleanField(required=False, label='Superuser (all permissions)')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        if commit:
            user.save()
        return user


from django.forms import ModelForm
from .models import Record


class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ["title", "description"]
        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}),
        }
