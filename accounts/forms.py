from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


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