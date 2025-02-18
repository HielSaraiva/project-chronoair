# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import PavilhaoModelForm, HorarioModelForm, SalaModelForm, ArCondicionadoModelForm
from .models import Pavilhao, Horario, Sala, ArCondicionado
from .mqtt import mqtt_publish


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
def listar_ares(request):
    pavilhoes = Pavilhao.objects.all()
    salas = Sala.objects.all()
    ares = ArCondicionado.objects.all()

    filtrarpavilhao = request.POST.get('pavilhao')
    filtrarsala = request.POST.get('sala')

    if filtrarpavilhao:
        ares = ares.filter(sala__pavilhao__id=filtrarpavilhao)
        salas = salas.filter(pavilhao__id=filtrarpavilhao)  # Atualiza as salas conforme o pavilhão
    if filtrarsala:
        ares = ares.filter(sala__id=filtrarsala)

    context = {
        'ares': ares,
        'pavilhoes': pavilhoes,
        'salas': salas,
        'filtrarpavilhao': filtrarpavilhao,
        'filtrarsala': filtrarsala,
    }

    return render(request, 'listar_ares.html', context)


@login_required
def listar_horarios(request):
    pavilhoes = Pavilhao.objects.all()
    salas = Sala.objects.all()
    turnos = [
        ('Madrugada', 'Madrugada'),
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
    ]

    dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    horas = sorted(set(horario.horario_inicio.hour for horario in Horario.objects.all()))

    filtrarpavilhao = request.POST.get('pavilhao')
    filtrarturno = request.POST.get('turno')
    filtrarsala = request.POST.get('sala')

    filtros = {}

    horarios = Horario.objects.none()

    if filtrarpavilhao:
        salas = salas.filter(pavilhao__id=filtrarpavilhao)

    if filtrarsala:
        filtros['sala'] = filtrarsala
        if filtrarturno:
            filtros['turno__icontains'] = filtrarturno
        if request.method == 'POST':
            horarios = Horario.objects.filter(**filtros).order_by("horario_inicio")

            # Adicionar duração a cada horário antes de enviar ao template
            for horario in horarios:
                horario.duracao = (horario.horario_fim.hour - horario.horario_inicio.hour) * 60 + (
                        horario.horario_fim.minute - horario.horario_inicio.minute)

    context = {
        'horarios': horarios,
        'pavilhoes': pavilhoes,
        'salas': salas,
        'turnos': turnos,
        'filtrarsala': filtrarsala,
        'filtrarpavilhao': filtrarpavilhao,
        'filtrarturno': filtrarturno,
        'dias_da_semana': dias_da_semana,
        'horas': horas,
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
    return render(request, 'criar_pavilhao.html', context)


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
        form = SalaModelForm()
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_sala.html', context)


@login_required
def criar_ar(request):
    # Validação e envio do formulário da sala
    if str(request.method) == 'POST':
        form = ArCondicionadoModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são validos
            form.save()  # Se os dados forem válidos, ele irá salvar
            messages.success(request,
                             'Ar-condicionado criado com sucesso!')
            return redirect('website:listar_ares')
    else:
        form = ArCondicionadoModelForm()
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_ar.html', context)


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
    return render(request, 'criar_horario.html', context)


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
    return render(request, 'criar_sala.html', context)


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
    return render(request, 'criar_horario.html', context)


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
    return render(request, 'criar_pavilhao.html', context)


@login_required
def editar_ares(request, pk):
    ar = ArCondicionado.objects.get(id=pk)

    if request.method == 'POST':
        form = ArCondicionadoModelForm(request.POST, instance=ar)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ar-condicionado editado com sucesso!')
            return redirect('website:listar_ares')
    else:
        form = ArCondicionadoModelForm(instance=ar)
    context = {'form': form, 'ar': ar}
    return render(request, 'criar_ar.html', context)


@login_required
def deletar_ares(request, pk):
    ar = ArCondicionado.objects.get(id=pk)

    if request.method == 'POST':
        ar.delete()
        messages.success(request,
                         'Ar-condicionado deletado com sucesso!')
        return redirect('website:listar_ares')
    context = {'ar': ar}
    return render(request, 'deletar_ares.html', context)


@login_required
def ajustar_ar(request, pk):
    ar = ArCondicionado.objects.get(id=pk)

    context = {
        'ar': ar
    }

    return render(request, 'ajustar_ar.html', context)


@login_required
def ajustar_sala(request, pk):
    sala = Sala.objects.get(id=pk)
    ares = ArCondicionado.objects.filter(sala=sala)
    ares_quantidade = ares.count()

    context = {
        'sala': sala,
        'ares': ares,
        'ares_quantidade': ares_quantidade
    }

    return render(request, 'ajustar_sala.html', context)


@login_required
def ajustes_ares(request, pk):
    ar = ArCondicionado.objects.get(id=pk)  # Obtém o ar-condicionado atualizado
    sala = ar.sala  # Pega a sala correta
    if request.method == 'POST':
        comando = request.POST.get('comando')
        topico = sala.topico_mqtt

        try:
            if comando in ['gravar_ligar', 'gravar_desligar']:
                mqtt_publish(topico, {"comando": comando})
                messages.success(request, f"Comando '{comando}' enviado com sucesso!")
            else:
                messages.error(request, "Comando inválido.")
        except Exception as e:
            messages.error(request, f"Erro ao enviar comando: {str(e)}")

        return redirect('website:ajustar_ar', pk=pk)


@login_required
def ajustes_salas(request, pk):
    sala = Sala.objects.get(id=pk)  # Obtém a sala

    if request.method == 'POST':
        comando = request.POST.get('comando')
        topico = sala.topico_mqtt

        try:
            if comando in ['ligar', 'desligar']:
                mqtt_publish(topico, {"comando": comando})
                messages.success(request, f"Comando '{comando}' enviado com sucesso!")
            else:
                messages.error(request, "Comando inválido.")
        except Exception as e:
            messages.error(request, f"Erro ao enviar comando: {str(e)}")

        return redirect('website:ajustar_sala', pk=pk)
