from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

# Create your views here.
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('admin:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form':form})

@require_POST
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('admin:index')
    
@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('admin:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('admin:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form':form})

@require_safe
def profile(request, username):
    User = get_user_model()
    person = User.objects.get(username=username)
    return render(request, 'accounts/profile.html', {'person':person})


@require_POST
def follow(request, user_pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    User = get_user_model()
    person = User.objects.get(pk = user_pk)
    if person != request.user:
        if person.followers.filter(pk=request.user.pk).exists():
            person.followers.remove(request.user)
        else:
            person.followers.add(request.user)
    return redirect('accounts:profile', username=person.username)
