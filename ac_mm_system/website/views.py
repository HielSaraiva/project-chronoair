# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import PavilhaoModelForm, HorarioModelForm, SalaModelForm
from .models import Pavilhao, Horario, Sala


@login_required
def pagina_inicial(request):
    return render(request, 'pagina_inicial.html')

@login_required
def listar_pavilhoes(request):
    context = {
        'pavilhoes': Pavilhao.objects.all()  # permite exibir todos os objetos 'pavilhão' que foram criados
    }
    return render(request, 'listar_pavilhoes.html', context)

@login_required
def listar_salas(request):
    pavilhoes = Pavilhao.objects.all()
    filtrarpavilhao = None

    if request.method == 'POST':
        filtrarpavilhao = request.POST.get('pavilhao')
        if filtrarpavilhao:
            salas = Sala.objects.filter(pavilhao__id=filtrarpavilhao)
        else:
            salas = Sala.objects.all()
    else:
        salas = Sala.objects.all()

    context = {
        'salas': salas,
        'pavilhoes': pavilhoes,
        'filtrarpavilhao': filtrarpavilhao
    }
    return render(request, 'listar_salas.html', context)

@login_required
def listar_ar(request):
    return render(request, 'listar_ar.html')

@login_required
def listar_horarios(request):
    pavilhoes = Pavilhao.objects.all()
    salas = Sala.objects.all()
    filtrarpavilhao = None
    filtrarturno = None
    filtrarsala = None
    turnos = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
    ]

    if request.method == 'POST':
        filtrarpavilhao = request.POST.get('pavilhao')
        filtrarturno = request.POST.get('turno')
        filtrarsala = request.POST.get('sala')

        # Criando um dicionário de filtros
        filtros = {}

        if filtrarpavilhao:
            filtros['pavilhao__id'] = filtrarpavilhao
        if filtrarturno:
            filtros['turno'] = filtrarturno
        if filtrarsala:
            filtros['sala'] = filtrarsala

        # Filtrando os horários com base nos filtros fornecidos
        horarios = Horario.objects.filter(**filtros)

    else:
        horarios = Horario.objects.all()

    context = {
        'horarios': horarios,
        'pavilhoes': pavilhoes,
        'salas': salas,
        'turnos': turnos,
        'filtrarsala': filtrarsala,
        'filtrarpavilhao': filtrarpavilhao,
        'filtrarturno': filtrarturno,
    }
    return render(request, 'listar_horarios.html', context)

@login_required
def criar_pavilhao(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = PavilhaoModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            form.save()  # Se os dados forem válidos ele irá salvar
            messages.success(request,
                             'Pavilhão criado com sucesso!')  # Exibe uma mensagem de sucesso, caso o pavilhão seja criado
            # form = PavilhaoModelForm()  # Cria um novo formulário vazio após salvar os dados
            return redirect('website:listar_pavilhoes')
        else:
            messages.error(request,
                           'Erro ao criar pavilhão')  # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = PavilhaoModelForm()
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_pavilhoes.html', context)

@login_required
def criar_horario(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = HorarioModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            form.save()  # Se os dados forem válidos ele irá salvar
            messages.success(request,
                             'Horário criado com sucesso!')  # Exibe uma mensagem de sucesso, caso o horário seja criado
            # form = HorarioModelForm()  # Cria um novo formulário vazio após salvar os dados
            return redirect('website:listar_horarios')
        else:
            messages.error(request,
                           'Erro ao criar horário')  # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = HorarioModelForm()
    context = {
        'form': form
    }
    return render(request, 'criar_horarios.html', context)

@login_required
def criar_sala(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = SalaModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            form.save()  # Se os dados forem válidos ele irá salvar
            messages.success(request,
                             'Sala criada com sucesso!')  # Exibe uma mensagem de sucesso, caso a sala seja criada
            # form = SalaModelForm()  # Cria um novo formulário vazio após salvar os dados
            return redirect('website:listar_salas')
        else:
            messages.error(request, 'Erro ao criar sala')  # Exibe uma mensagem de erro, caso os dados não sejam válidos
    else:
        form = SalaModelForm()
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_salas.html', context)

@login_required
def editar_salas(request, pk):
    sala = Sala.objects.get(id=pk)

    if request.method == 'POST':
        form = SalaModelForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Sala editada com sucesso!')
            return redirect('website:listar_salas')
    else:
        form = SalaModelForm(instance=sala)
    context = {'form': form, 'sala': sala}
    return render(request, 'criar_salas.html', context)

@login_required
def deletar_salas(request, pk):
    sala = Sala.objects.get(id=pk)
    if request.method == 'POST':
        sala.delete()
        messages.success(request,
                         'Sala deletada com sucesso!')
        return redirect('website:listar_salas')
    context = {
        'sala': sala
    }
    return render(request, 'deletar_salas.html', context)

@login_required
def deletar_horarios(request, pk):
    horario = Horario.objects.get(id=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request,
                         'Horário deletado com sucesso!')
        return redirect('website:listar_horarios')
    context = {
        'horario': horario
    }
    return render(request, 'deletar_horarios.html', context)

@login_required
def editar_horarios(request, pk):
    horario = Horario.objects.get(id=pk)

    if request.method == 'POST':
        form = HorarioModelForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Horário editado com sucesso!')
            return redirect('website:listar_horarios')
    else:
        form = HorarioModelForm(instance=horario)
    context = {'form': form, 'horario': horario}
    return render(request, 'criar_horarios.html', context)

@login_required
def deletar_pavilhoes(request, pk):
    pavilhao = Pavilhao.objects.get(id=pk)
    if request.method == 'POST':
        pavilhao.delete()
        messages.success(request,
                         'Pavilhão deletado com sucesso!')
        return redirect('website:listar_pavilhoes')
    context = {
        'pavilhao': pavilhao
    }
    return render(request, 'deletar_pavilhoes.html', context)

@login_required
def editar_pavilhoes(request, pk):
    pavilhao = Pavilhao.objects.get(id=pk)

    if request.method == 'POST':
        form = PavilhaoModelForm(request.POST, instance=pavilhao)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Pavilhão editado com sucesso!')
            return redirect('website:listar_pavilhoes')
    else:
        form = PavilhaoModelForm(instance=pavilhao)
    context = {'form': form, 'pavilhao': pavilhao}
    return render(request, 'criar_pavilhoes.html', context)
