from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, PasswordInput, EmailInput, Textarea, CheckboxInput

INPUT_CLASSES = (
    "w-full rounded-2xl border border-white/15 bg-slate-950/60 px-4 py-3 text-sm "
    "text-white placeholder:text-slate-500 focus:border-sky-300 focus:outline-none "
    "focus:ring-2 focus:ring-sky-400/40"
)

TEXTAREA_CLASSES = (
    "w-full rounded-2xl border border-white/15 bg-slate-950/60 px-4 py-3 text-sm "
    "text-white placeholder:text-slate-500 focus:border-sky-300 focus:outline-none "
    "focus:ring-2 focus:ring-sky-400/40"
)

CHECKBOX_CLASSES = "h-5 w-5 rounded border-white/25 bg-slate-900 text-sky-400 focus:ring-sky-400"

# Register form
class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styled_fields = {
            'username': {'placeholder': 'Username', 'autocomplete': 'username'},
            'email': {'placeholder': 'Email', 'autocomplete': 'email'},
            'password1': {'placeholder': 'Password', 'autocomplete': 'new-password'},
            'password2': {'placeholder': 'Confirm password', 'autocomplete': 'new-password'},
        }
        for name, extra_attrs in styled_fields.items():
            field = self.fields.get(name)
            if not field:
                continue
            classes = field.widget.attrs.get('class', '')
            if INPUT_CLASSES not in classes:
                field.widget.attrs['class'] = f"{INPUT_CLASSES} {classes}".strip()
            field.widget.attrs.update(extra_attrs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Username'}),
            'email': EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email'}),
            'password1': PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Password'}),
            'password2': PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Confirm Password'}),
        }

        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }

# Login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Password'})
    )


class AdminCreateUserForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email'}),
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Admin (can access staff area)',
        widget=CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
    )
    is_superuser = forms.BooleanField(
        required=False,
        label='Superuser (all permissions)',
        widget=CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
    )

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
            'title': TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Title'}),
            'description': Textarea(
                attrs={
                    'class': TEXTAREA_CLASSES,
                    'rows': 4,
                    'placeholder': 'Description',
                }
            ),
        }
