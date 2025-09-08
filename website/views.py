from django.shortcuts import render
from .forms import CreateUserForm, LoginForm

# Create your views here.
def home(request):
    return render(request, 'pages/index.html')

def login(request):
    return render(request, 'pages/login.html')

def register(request):
    # Make a form from forms.py
    
    form = CreateUserForm()
    if request.method == 'POST':
        # Make a form with the data filled by the user

        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'pages/register.html', context)

