from django.shortcuts import render, redirect
from divulgar.models import Pet, Raca
from .models import PedidoAdocao
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.core.mail import send_mail


def listar_pets(request):
    pets = Pet.objects.filter(status="P")
    lista_racas = Raca.objects.filter(pet__in=pets).distinct()

    # Armazenar as informações digitas na página de cadastro e devolver na tela se houver algum erro de incosistência
    request.session['form_data'] = request.GET
    form_data = request.session.get('form_data', {})
    
    if request.method == "GET":
        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')

        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter:
            pets = pets.filter(raca__id=raca_filter)

        return render(request, 'listar_pets.html', {'form_data': form_data, 'pets': pets, 'lista_racas': lista_racas, 'cidade': cidade, 'raca_filter': raca_filter})
    
def ver_pet(request, id):
    if request.method == "GET":
        pet = Pet.objects.get(id = id)
        return render(request, 'ver_pet.html', {'pet': pet})    
    
def pedido_adocao(request, id_pet):
    pet = Pet.objects.filter(id=id_pet).filter(status="P")

    if not pet.exists():
        messages.add_message(request, constants.ERROR, 'Esse pet já foi adotado :)')
        return redirect('/adotar')

    pedido = PedidoAdocao(pet=pet.first(),
                          usuario=request.user,
                          data=datetime.now())

    pedido.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado, você receberá um e-mail caso ele seja aprovado.')
    return redirect('/adotar')    

def ver_pedido_adocao(request):
    if request.method == "GET":
        pedidos = PedidoAdocao.objects.filter(usuario=request.user).filter(status="AG")
        return render(request, 'ver_pedido_adocao.html', {'pedidos': pedidos})
    

def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    pet = pedido.pet
    if status == "A":
        pedido.status = 'AP'
        pet.status = 'A'
        pet.save()
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'

    pedido.save()

    
    print(pedido.usuario.email)
    email = send_mail(
        'Sua adoção foi processada',
        string,
        'caio@pythonando.com.br',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/adotar/ver_pedido_adocao')    

