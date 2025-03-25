from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import LoginForm, RegisterForm

# Create your views here.
def main(request):
    return render(request, 'home_index.html')

def play(request):
    return render(request, 'play.html')

def my_tournaments(request):
    return render(request, 'my_tournaments.html')

def rules(request):
    return render(request, 'rules.html')






# .......................................
# Авторизация и регистрация



def login_register_view(request):
    if request.method == 'POST':
        if 'username' in request.POST and 'password1' in request.POST:
            # Это регистрация
            register_form = RegisterForm(request.POST)
            login_form = LoginForm()
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('home')  # поменяй на нужную тебе страницу
            else:
                messages.error(request, 'Ошибка при регистрации.')
        else:
            # Это вход
            login_form = LoginForm(request, data=request.POST)
            register_form = RegisterForm()
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('home')  # поменяй на нужную тебе страницу
            else:
                messages.error(request, 'Неверные данные для входа.')
    else:
        login_form = LoginForm()
        register_form = RegisterForm()

    return render(request, 'login_register.html', {
        'login_form': login_form,
        'register_form': register_form,
    })





def logout_view(request):
    logout(request)
    return redirect('tennis_app:login_register')  # или другая нужная страница