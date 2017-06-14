""" standard Django views module for back-end logic """
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from Elisio.models import Author

CONTEXT = {}

def index(request):
    """ return index page """
    CONTEXT['authors'] = Author.objects.filter(opus__book__gt=0).distinct()
    return render(request, 'index.html', CONTEXT)

def batch(request):
    """ return batch page """
    return render(request, 'batch.html', CONTEXT)

def help_page(request):
    """ return help page """
    return render(request, 'help.html', CONTEXT)

def about(request):
    """ return about page """
    return render(request, 'about.html', CONTEXT)

def profile(request):
    """ return profile page if logged in """
    if request.user.is_authenticated:
        return render(request, 'profile.html', CONTEXT)
    return HttpResponseRedirect('/')

def inlog(request):
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
    return render(request, 'login.html', CONTEXT)

def outlog(request):
    redirecter = request.GET.get('next', '/')
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(redirecter)

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            login(request, user)
            return index(request)
        except Exception as e:
            # TODO: handle in error message
            pass
    return render(request, 'register.html', CONTEXT)

def manage(request):
    if request.user.is_superuser:
        return render(request, 'manage.html', CONTEXT)
    return HttpResponseRedirect('/')
