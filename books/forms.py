from django import forms
from .models import Book, Thread

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('user',)
        labels = {
            'title': '도서 제목',
            'description': '설명',
            'customer_review_rank': '회원 리뷰 평점 (0~5)',
            'author': '저자',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'customer_review_rank': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 5 }),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ('title', 'content', 'read_date')
        labels = {
            'title': '제목',
            'content': '내용',
            'read_date': '독서일',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'read_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

