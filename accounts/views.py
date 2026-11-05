from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile', username=request.user.username)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form':form})

@require_POST
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('accounts:login')  # TODO: B가 push하면 'books:index'로 교체
    
@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile', username=request.user.username)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('accounts:profile', username=request.user.username)
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

@require_safe
def people(request):
    User = get_user_model()
    persons = User.objects.all()
    if request.user.is_authenticated:
        persons = persons.exclude(pk=request.user.pk)
    return render(request, 'accounts/people.html', {'persons':persons})

@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance =request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile', username=request.user)
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/update.html', {'form':form})