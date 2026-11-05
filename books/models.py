from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    customer_review_rank = models.FloatField(
        validators = [MinValueValidator(0), MaxValueValidator(5)]
    )
    author = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    def __str__(self):
        return self.title

class Thread(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    read_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_threads')

    def __str__(self):
        return self.title


    
