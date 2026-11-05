from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_safe 
from .forms import BookForm, ThreadForm
from .models import Book, Thread


@require_safe
def index(request):
    books = Book.objects.order_by('-pk')
    context = {'books': books}
    return render(request, 'books/index.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('books:detail', book.pk)
    else: 
        form = BookForm()
    context = {'form': form}  
    return render(request, 'books/create.html', context)  


@require_safe
def detail(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    threads = book.thread_set.order_by('-pk')
    context = {
        'book': book,
        'threads': threads,
    }
    return render(request, 'books/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def update(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.user != book.user:
        return redirect('books:detail', book.pk)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('books:detail', book.pk) 
    else:  # ← 수정 4
        form = BookForm(instance=book)
    context = {  # ← 수정 4
        'book': book,
        'form': form,
    }
    return render(request, 'books/update.html', context) 


@login_required
@require_POST
def delete(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.user == book.user:
        book.delete()
        return redirect('books:index') 
    return redirect('books:detail', book.pk) 

@login_required
@require_http_methods(['GET', 'POST'])
def thread_create(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book = book
            thread.user = request.user
            thread.save()
            return redirect('books:thread_detail', thread.pk)
    else:
        form = ThreadForm()
    context = {
        'book': book,
        'form': form,
    }
    return render(request, 'books/thread_create.html', context)

@require_safe
def thread_detail(request, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    context = {'thread': thread}
    return render(request, 'books/thread_detail.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def thread_update(request, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    if request.user != thread.user:
        return redirect('books:thread_detail', thread.pk)

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('books:thread_detail', thread.pk)
    else:
        form = ThreadForm(instance=thread)
    context = {
        'thread' : thread,
        'form' : form,
    }
    return render(request, 'books/thread_update.html', context)

@login_required
@require_POST
def thread_delete(request, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    book_pk = thread.book.pk
    if request.user == thread.user:
        thread.delete()
        return redirect('books:detail', book_pk)
    return redirect('books:thread_detail', thread_pk)
