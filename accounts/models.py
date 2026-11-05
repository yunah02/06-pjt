from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    name = models.CharField('카테고리', max_length=50)

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]

    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField('나이', null=True, blank=True)
    weekly_reading_time = models.PositiveIntegerField('주간 평균 독서 시간(시간)', null=True, blank=True)
    yearly_reading_count = models.PositiveIntegerField('연간 독서량(권)', null=True, blank=True)
    profile_image = models.ImageField('프로필 사진', upload_to='profile/', blank=True)

    followings = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
    )
    preferred_categories = models.ManyToManyField(
        Category,
        related_name='preferred_users',
        blank=True,
    )