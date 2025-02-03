from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pet, Tag, Raca
from django.contrib import messages
from django.contrib.messages import constants
from .utils import buscar_endereco, extrair_numeros
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adotar.models import PedidoAdocao

@login_required
def novo_pet(request):

    opcoes_tags = Tag.objects.all()
    opcoes_racas = Raca.objects.all()

    if request.method == "GET":
        return render(request, 'novo_pet.html', {'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas})
    elif request.method == "POST":
        foto = request.FILES.get('foto')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        cep = request.POST.get('cep')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        telefone = request.POST.get('telefone')
        tags = request.POST.getlist('tags')
        raca = request.POST.get('raca')

        # Armazenar as informações digitas na página de cadastro e devolver na tela se houver algum erro de incosistência
        request.session['form_data'] = request.POST
        form_data = request.session.get('form_data', {})

        tag_form = []
        for tag_id in tags:
            tag_form.append(tag_id)

        if not foto:
            messages.add_message(request, constants.ERROR, 'A foto do pet é obrigatória')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})

        if not nome:
            messages.add_message(request, constants.ERROR, 'O nome do pet é obrigatório')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not descricao:
            messages.add_message(request, constants.ERROR, 'A descrição é obrigatória')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not cep:
            messages.add_message(request, constants.ERROR, 'O CEP é obrigatório')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        cep = extrair_numeros(cep)
        
        if not estado:
            messages.add_message(request, constants.ERROR, 'O estado é obrigatório')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not cidade:
            messages.add_message(request, constants.ERROR, 'A cidade é obrigatória')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not telefone:
            messages.add_message(request, constants.ERROR, 'O telefone é obrigatório')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not tags:
            messages.add_message(request, constants.ERROR, 'As tags são obrigatórias')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        if not raca:
            messages.add_message(request, constants.ERROR, 'A raça é obrigatória')
            return render(request, 'novo_pet.html', {'form_data': form_data, 'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas, 'tag_form': tag_form})
        
        pet = Pet(
            usuario=request.user,
            foto=foto,
            nome=nome,
            descricao=descricao,
            cep=cep,
            estado=estado,
            cidade=cidade,
            telefone=telefone,
            raca_id=raca,
        )

        pet.save()
        
        for tag_id in tags:
            tag = Tag.objects.get(id=tag_id)
            pet.tags.add(tag)

        pet.save()
        opcoes_tags = Tag.objects.all()
        opcoes_racas = Raca.objects.all()

        del request.session['form_data']

        messages.add_message(request, constants.SUCCESS, 'Novo pet cadastrado')
        return render(request, 'novo_pet.html', {'opcoes_tags': opcoes_tags, 'opcoes_racas': opcoes_racas})
    
@csrf_exempt
def buscar_endereco_view(request):
    if request.method == 'POST':
        cep = request.POST.get('cep')

        endereco = buscar_endereco(cep)  # Chame a função de utils.py

        if endereco:
            localidade = endereco['localidade']
            uf = endereco['uf']
            return JsonResponse({'status': 'sucesso', 'localidade': localidade, 'uf': uf})
        else:
            return JsonResponse({'status': 'erro', 'message': 'CEP inválido ou erro ao buscar o endereço'})

    return JsonResponse({'status': 'falha'})

@login_required
def seus_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(usuario=request.user)
        return render(request, 'seus_pets.html', {'pets': pets})
    
@login_required
def remover_pet(request, id):
    pet = Pet.objects.get(id=id)

    if not pet.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pet não é seu!')
        return redirect('/divulgar/seus_pets')

    pet.delete()
    messages.add_message(request, constants.SUCCESS, 'Removido com sucesso.')
    return redirect('/divulgar/seus_pets')    

def dashboard(request):
    if request.method == "GET":
        return render(request, 'dashboard.html')
    

@csrf_exempt
def api_adocoes_por_raca(request):
    pets = Pet.objects.all()
    racas = Raca.objects.filter(pet__in=pets).distinct()

    qtd_adocoes = []

    for raca in racas:
        adocoes = PedidoAdocao.objects.filter(pet__raca=raca).count()
        qtd_adocoes.append(adocoes)
    racas = [raca.raca for raca in racas]

    data = {'qtd_adocoes': qtd_adocoes,
            'labels': racas}

    return JsonResponse(data)    