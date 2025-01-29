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
    pavilhoes = Pavilhao.objects.all()
    if request.method == 'POST':
        filtrarpavilhao = request.POST.get('pavilhao')
        salas = Sala.objects.filter(pavilhao__id=filtrarpavilhao)
    else:
        salas = Sala.objects.all()

    context = {
        'salas': salas,
        'pavilhoes': pavilhoes,
    }
    return render(request, 'listasalas.html', context)


def listaAr_View(request):
    return render(request, 'listaar.html')


def listaHorarios_View(request):
    pavilhoes = Pavilhao.objects.all()
    if request.method == 'POST':
        filtrarpavilhao = request.POST.get('pavilhao')
        horarios = Horario.objects.filter(pavilhao__id=filtrarpavilhao)
    else:
        horarios = Horario.objects.all()

    context = {
        'horarios': horarios,
        'pavilhoes': pavilhoes,
    }
    return render(request, 'listahorarios.html', context)


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

def editarSalas_View(request, pk):
    sala = Sala.objects.get(id=pk)

    if request.method == 'POST':
        form = SalaModelForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect('listasalas')
    else:
        form = SalaModelForm(instance=sala)
    context = {'form': form, 'sala': sala}
    return render(request, 'criarsalas.html', context)

def deletarSalas_View(request, pk):
    sala = Sala.objects.get(id=pk)
    if request.method == 'POST':
        sala.delete()
        return redirect('listasalas')
    context = {
        'sala': sala
    }
    return render(request, 'deletarsalas.html', context)

def deletarHorarios_View(request, pk):
    horario = Horario.objects.get(id=pk)
    if request.method == 'POST':
        horario.delete()
        return redirect('listahorarios')
    context = {
        'horario': horario
    }
    return render(request, 'deletarhorarios.html', context)

def editarHorarios_View(request, pk):
    horario = Horario.objects.get(id=pk)

    if request.method == 'POST':
        form = HorarioModelForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('listahorarios')
    else:
        form = HorarioModelForm(instance=horario)
    context = {'form': form, 'horario': horario}
    return render(request, 'criarhorarios.html', context)

def deletarPavilhoes_View(request, pk):
    pavilhao = Pavilhao.objects.get(id=pk)
    if request.method == 'POST':
        pavilhao.delete()
        return redirect('listapavilhoes')
    context = {
        'pavilhao': pavilhao
    }
    return render(request, 'deletarpavilhoes.html', context)

def editarPavilhoes_View(request, pk):
    pavilhao = Pavilhao.objects.get(id=pk)

    if request.method == 'POST':
        form = PavilhaoModelForm(request.POST, instance=pavilhao)
        if form.is_valid():
            form.save()
            return redirect('listapavilhoes')
    else:
        form = PavilhaoModelForm(instance=pavilhao)
    context = {'form': form, 'pavilhao':pavilhao}
    return render(request, 'criarpavilhoes.html', context)