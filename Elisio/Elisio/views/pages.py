""" standard Django views module for back-end logic """
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from Elisio.engine.verse.VerseType import VerseForm
from Elisio.models.forms import AuthorForm, OpusForm
from Elisio.models import Author, Opus, Book, Poem
import Elisio.batchjob
from Elisio.numerals import roman_to_int


def index_page(request):
    """ return index page """
    return render(request, 'index.html')


def batch_page(request):
    """ return batch page """
    return render(request, 'batch.html')


def help_page(request):
    """ return help page """
    return render(request, 'help.html')


def about_page(request):
    """ return about page """
    return render(request, 'about.html')


def profile_page(request):
    """ return profile page if logged in """
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    return HttpResponseRedirect('/')


def login_page(request):
    redirecter = request.GET.get('next', '/')
    if 'login' in redirecter:
        redirecter = '/'
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        return HttpResponseRedirect(redirecter)
    return render(request, 'login.html')


def logout_page(request):
    redirecter = request.GET.get('next', '/')
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(redirecter)


def register_page(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            login(request, user)
            return index_page(request)
        except (IntegrityError, Exception):
            # TODO: handle in error message
            pass
    return render(request, 'register.html')


def manage_page(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        return render(request, 'manage.html')
    split = Elisio.batchjob.clean_name(request.POST['poem'])
    try:
        author = Elisio.batchjob.find_author(split[0])
    except Author.DoesNotExist:
        return render(request, 'manage.html', {'form': AuthorForm(data={'abbreviation': split[0]})})
    try:
        opus = Elisio.batchjob.find_opus(author, split[1])
    except Opus.DoesNotExist:
        form = OpusForm(data={'author': author, 'abbreviation': split[1]})
        return render(request, 'manage.html', {'form': form})
    try:
        book_number = roman_to_int(split[2])
    except TypeError:
        book_number = int(split[2])
    try:
        book = Elisio.batchjob.find_book(opus, book_number)
        try:
            poem = Elisio.batchjob.find_poem(book, split[3], True)
        except IndexError:
            poem = Elisio.batchjob.find_poem(book, create=True)
    except Book.DoesNotExist:
        book = Book(opus=opus, number=book_number)
        book.save()
        poem_number = int(split[3]) if len(split) > 3 else 1
        try:
            verse_form = VerseForm[request.POST['verseForm']]
        except KeyError:
            verse_form = VerseForm.HEXAMETRIC
        poem = Poem(book=book, number=poem_number, verseForm=verse_form)
    if poem and not poem.pk:
        poem.save()
    lines = request.POST['fulltext'].replace('\r\n', '\n').split('\n')
    Elisio.batchjob.create_verses(poem, lines)
    return render(request, 'manage.html')
