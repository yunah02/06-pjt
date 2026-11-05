from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q


# Create your views here.
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('books:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('books:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('books:index')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('books:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('books:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@require_safe
def profile(request, username):
    User = get_user_model()
    try:
        person = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('존재하지 않는 사용자입니다.')
    return render(request, 'accounts/profile.html', {'person': person})


@require_POST
def follow(request, user_pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    User = get_user_model()
    try:
        person = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        raise Http404('존재하지 않는 사용자입니다.')

    if person != request.user:
        if person.followers.filter(pk=request.user.pk).exists():
            person.followers.remove(request.user)
        else:
            person.followers.add(request.user)
    return redirect('accounts:profile', username=person.username)


@require_safe
def people(request):
    User = get_user_model()
    persons = User.objects.annotate(
        follower_count=Count('followers', distinct=True)
    ).order_by('-follower_count', 'username')

    recommended = []
    if request.user.is_authenticated:
        persons = persons.exclude(pk=request.user.pk)
        my_categories = request.user.preferred_categories.all()
        recommended = (
            persons.exclude(pk__in=request.user.followings.all())
            .annotate(
                common_count=Count(
                    'preferred_categories',
                    filter=Q(preferred_categories__in=my_categories),
                    distinct=True,
                )
            )
            .order_by('-common_count', '-follower_count', 'username')[:5]
        )

    return render(request, 'accounts/people.html', {
        'persons': persons,
        'recommended': recommended,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('books:index')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/update.html', {'form': form})


@require_POST
def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)
    return redirect('books:index')


@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('books:index')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})