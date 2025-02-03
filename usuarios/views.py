from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from .utils import gerar_senha, analisar_senha
from django.contrib.auth import authenticate, login, logout


from django.contrib.auth.models import User

def cadastro(request):

    senha_sugerida = gerar_senha(10)

    if request.method == "GET":
        return render(request, 'cadastro.html', {'senha_sugerida': senha_sugerida})
    elif request.method == "POST":
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Armazenar as informações digitas na página de cadastro e devolver na tela se houver algum erro de incosistência
        request.session['form_data'] = request.POST
        form_data = request.session.get('form_data', {})
        #
        if not nome :
            messages.add_message(request, constants.ERROR, 'Nome obrigatório')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        users = User.objects.filter(username=nome)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'Este usuário já está cadastrado')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not email :
            messages.add_message(request, constants.ERROR, 'Email obrigatório')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        users_email = User.objects.filter(email=email)
        
        if users_email :
            messages.add_message(request, constants.ERROR, 'Email já cadastrado')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if '@' not in email :
            messages.add_message(request, constants.ERROR, 'Digite um email válido')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        validacoes_senha = analisar_senha(senha, confirmar_senha)

        if not validacoes_senha['confirmar_senha']:
            messages.add_message(request, constants.ERROR, 'A senha e confirmar senha devem ser iguais')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not validacoes_senha['tamanho']:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos 8 dígitos')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not validacoes_senha['especial']:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos um caracter especial')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not validacoes_senha['maiuscula']:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos uma letra maiúscula')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not validacoes_senha['minuscula']:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos uma letra minúscula')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        if not validacoes_senha['numeros']:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos um número')
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})
        
        try:
            user = User.objects.create_user(
                username=nome,
                email=email,
                password=senha,
            )
            return redirect('/auth/login')
        except:
            return render(request, 'cadastro.html', {'form_data': form_data, 'senha_sugerida': senha_sugerida})

def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')
        user = authenticate(username=nome,
                            password=senha)

        if user is not None:
            login(request, user)
            return redirect('/divulgar/novo_pet')
        else:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
            return render(request, 'login.html')

def sair(request):
    auth.logout(request)
    return redirect('/auth/login')
