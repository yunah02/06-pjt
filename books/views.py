from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import BookForm, ThreadForm, CommentForm
from .models import Book, Thread, Comment
from django.http import Http404
from accounts.models import Category
from .ai import fill_author_info

@require_safe
def index(request):
    categories = Category.objects.all()
    selected = request.GET.get('category')
    books = Book.objects.order_by('-pk')
    if selected and selected.isdigit():
        selected = int(selected)
        books = books.filter(category_id=selected)
    else:
        selected = None
    context = {
        'books': books,
        'categories': categories,
        'selected': selected,
    }
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
            fill_author_info(book)
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

@require_POST
def like(request, thread_pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    try:
        thread = Thread.objects.get(pk=thread_pk)
    except Thread.DoesNotExist:
        raise Http404('존재하지 않는 쓰레드입니다.')

    if thread.like_users.filter(pk=request.user.pk).exists():
        thread.like_users.remove(request.user)  
    else:
        thread.like_users.add(request.user)   
    return redirect('books:thread_detail', thread_pk=thread.pk)

@login_required
@require_POST
def comment_create(request, thread_pk):
    try:
        thread = Thread.objects.get(pk=thread_pk)
    except Thread.DoesNotExist:
        raise Http404('존재하지 않는 쓰레드입니다.')

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.thread = thread
        comment.user = request.user
        comment.save()
    return redirect('books:thread_detail', thread_pk=thread.pk)


@login_required
@require_POST
def comment_delete(request, comment_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
    except Comment.DoesNotExist:
        raise Http404('존재하지 않는 댓글입니다.')

    thread_pk = comment.thread.pk
    if comment.user == request.user:   # 본인 댓글만 삭제
        comment.delete()
    return redirect('books:thread_detail', thread_pk=thread_pk)