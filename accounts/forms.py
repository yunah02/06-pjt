from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            'username', 'password1', 'password2',
            'email', 'last_name', 'first_name',
            'gender', 'age',
            'weekly_reading_time', 'yearly_reading_count',
            'profile_image',
        )
        labels = {'preferred_categories': '선호 카테고리'}
        widgets = {'preferred_categories': forms.CheckboxSelectMultiple()}


class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = (
            'username', 'email', 'last_name', 'first_name',
            'gender', 'age',
            'weekly_reading_time', 'yearly_reading_count',
            'profile_image',
        )
        labels = {'preferred_categories': '선호 카테고리'}
        widgets = {'preferred_categories': forms.CheckboxSelectMultiple()}