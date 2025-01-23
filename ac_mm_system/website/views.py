# Create your views here.
from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import PavilhaoModelForm, HorarioModelForm, SalaModelForm
from .models import Pavilhao, Horario, Sala

def login_user(request):
    return render(request, 'login.html')


def logIn_View(request):
    return render(request, 'login.html')


def paginaInicial_View(request):
    return render(request, 'paginainicial.html')


def listaPavilhoes_View(request):
    context = {
        'pavilhoes': Pavilhao.objects.all() #permite exibir todos os objetos 'pavilhão' que foram criados
    }
    return render(request, 'listapavilhoes.html', context)


def listaSalas_View(request):
    context = {
        'salas': Sala.objects.all() #permite exibir todos os objetos 'sala' que foram criados
    }
    return render(request, 'listasalas.html', context)


def listaAr_View(request):
    return render(request, 'listaar.html')


def listaHorarios_View(request):
    context = {
        'horarios': Horario.objects.all() #permite exibir todos os objetos 'horario' que foram criados
    }
    return render(request, 'listahorarios.html', context)


def listaUsuarios_View(request):
    return render(request, 'listausuarios.html')


def criarPavilhao_View(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = PavilhaoModelForm(request.POST)
        if form.is_valid(): # Verifica se os dados inseridos são válidos
            form.save() # Se os dados forem válidos ele irá salvar
            messages.success(request, 'Pavilhão criado com sucesso!') # Exibe uma mensagem de sucesso, caso o pavilhão seja criado
            form = PavilhaoModelForm() # Cria um novo formulário vazio após salvar os dados
        else:
            messages.error(request, 'Erro ao criar pavilhão') # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = PavilhaoModelForm()
    context = {
        'form': form # Passa o formulário para o contexto do template
    }
    return render(request, 'criarpavilhoes.html', context)


def criarHorario_View(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = HorarioModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            form.save()  # Se os dados forem válidos ele irá salvar
            messages.success(request, 'Horario criado com sucesso!')  # Exibe uma mensagem de sucesso, caso o horário seja criado
            form = HorarioModelForm() # Cria um novo formulário vazio após salvar os dados
        else:
            messages.error(request, 'Erro ao criar horário') # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = HorarioModelForm()
    context = {
        'form': form
    }
    return render(request, 'criarhorarios.html', context)


def criarSala_View(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = SalaModelForm(request.POST)
        if form.is_valid(): # Verifica se os dados inseridos são válidos
            form.save() # Se os dados forem válidos ele irá salvar
            messages.success(request, 'Sala criada com sucesso!') # Exibe uma mensagem de sucesso, caso a sala seja criada
            form = SalaModelForm()  # Cria um novo formulário vazio após salvar os dados
        else:
            messages.error(request, 'Erro ao criar sala') # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = SalaModelForm()
    context = {
        'form': form # Passa o formulário para o contexto do template
    }
    return render(request, 'criarsalas.html', context)