# Create your views here.
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from .forms import PavilhaoModelForm, HorarioModelForm, SalaModelForm, ArCondicionadoModelForm, GraficoModelForm
from .models import Pavilhao, Horario, Sala, ArCondicionado, Grafico
from .mqtt import mqtt_publish

from collections import OrderedDict
import json
from chartjs.views.lines import BaseLineChartView


@login_required
def listar_pavilhoes(request):
    pavilhoes = Pavilhao.objects.filter(usuario=request.user).order_by(Lower('nome'))

    context = {
        'pavilhoes': pavilhoes
    }
    return render(request, 'listar_pavilhoes.html', context)


@login_required
def listar_salas(request):
    pavilhoes = Pavilhao.objects.filter(usuario=request.user).order_by(Lower('nome'))

    filtrarpavilhao = None

    if request.method == 'POST':
        filtrarpavilhao = request.POST.get('pavilhao')
        if filtrarpavilhao:
            salas = Sala.objects.filter(pavilhao__uuid=filtrarpavilhao).order_by(Lower('nome'))
        else:
            salas = Sala.objects.filter(pavilhao__usuario=request.user).order_by(Lower('pavilhao__nome'), Lower('nome'))
    else:
        salas = Sala.objects.filter(pavilhao__usuario=request.user).order_by(Lower('pavilhao__nome'), Lower('nome'))

    context = {
        'salas': salas,
        'pavilhoes': pavilhoes,
        'filtrarpavilhao': filtrarpavilhao
    }
    return render(request, 'listar_salas.html', context)


@login_required
def listar_ares(request):
    pavilhoes = Pavilhao.objects.filter(usuario=request.user).order_by(Lower('nome'))
    salas = Sala.objects.filter(pavilhao__usuario=request.user).order_by(Lower('nome'))
    ares = ArCondicionado.objects.filter(sala__pavilhao__usuario=request.user)

    filtrarpavilhao = request.POST.get('pavilhao')
    filtrarsala = request.POST.get('sala')

    if filtrarpavilhao:
        salas = salas.filter(pavilhao__uuid=filtrarpavilhao).order_by(Lower('nome'))
        ares = ares.filter(sala__pavilhao__uuid=filtrarpavilhao)

    if filtrarsala:
        ares = ares.filter(sala__uuid=filtrarsala)

    ares = ares.order_by(
        Lower('sala__pavilhao__nome'),
        Lower('sala__nome'),
        Lower('nome')
    )

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
    pavilhoes = Pavilhao.objects.filter(usuario=request.user).order_by(Lower('nome'))
    salas = Sala.objects.filter(pavilhao__usuario=request.user).order_by(Lower('nome'))
    turnos = [
        ('Madrugada', 'Madrugada'),
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
    ]

    dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    horas = sorted(
        set(horario.horario_inicio.hour for horario in Horario.objects.filter(sala__pavilhao__usuario=request.user)))

    filtrarpavilhao = request.POST.get('pavilhao')
    filtrarturno = request.POST.get('turno')
    filtrarsala = request.POST.get('sala')

    filtros = {}

    horarios = Horario.objects.none()

    if filtrarpavilhao:
        salas = salas.filter(pavilhao__uuid=filtrarpavilhao)

    if filtrarsala:
        filtros['sala__uuid'] = filtrarsala
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
    if request.method == 'POST':
        form = PavilhaoModelForm(request.POST)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            try:
                novo_pavilhao = form.save(commit=False)
                novo_pavilhao.usuario = request.user
                novo_pavilhao.save()
                messages.success(request,
                                 'Pavilhão criado com sucesso!')  # Exibe uma mensagem de sucesso, caso o pavilhão seja criado

                return redirect('website:listar_pavilhoes')
            except IntegrityError:
                messages.error(request, "Você já tem um pavilhão com esse nome.")
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
    if request.method == 'POST':
        form = SalaModelForm(request.POST, usuario=request.user)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            try:
                form.save()
                messages.success(request,
                                 'Sala criada com sucesso!')  # Exibe uma mensagem de sucesso, caso a sala seja criada
                return redirect('website:listar_salas')
            except IntegrityError:
                messages.error(request, "Você já tem uma sala com esse nome neste pavilhão.")
    else:
        form = SalaModelForm(usuario=request.user)
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_sala.html', context)


@login_required
def criar_ar(request):
    # Validação e envio do formulário da sala
    if request.method == 'POST':
        form = ArCondicionadoModelForm(request.POST, usuario=request.user)
        if form.is_valid():  # Verifica se os dados inseridos são validos
            try:
                form.save()  # Se os dados forem válidos, ele irá salvar
                messages.success(request,
                                 'Ar-condicionado criado com sucesso!')
                return redirect('website:listar_ares')
            except IntegrityError:
                messages.error(request, "Você já tem um ar-condicionado com esse nome nesta sala.")
    else:
        form = ArCondicionadoModelForm(usuario=request.user)
    context = {
        'form': form  # Passa o formulário para o contexto do template
    }
    return render(request, 'criar_ar.html', context)


@login_required
def criar_horario(request):
    # Validação e envio do formulário da sala
    if request.method == 'POST':
        form = HorarioModelForm(request.POST, usuario=request.user)
        if form.is_valid():  # Verifica se os dados inseridos são válidos
            form.save()  # Se os dados forem válidos ele irá salvar
            messages.success(request,
                             'Horário criado com sucesso!')  # Exibe uma mensagem de sucesso, caso o horário seja criado
            # form = HorarioModelForm()  # Cria um novo formulário vazio após salvar os dados
            return redirect('website:listar_horarios')
    else:
        form = HorarioModelForm(usuario=request.user)
    context = {
        'form': form
    }
    return render(request, 'criar_horario.html', context)


@login_required
def editar_salas(request, uuid):
    sala = get_object_or_404(Sala, uuid=uuid)
    pavilhao = sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

    if request.method == 'POST':
        form = SalaModelForm(request.POST, instance=sala, usuario=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,
                                 'Sala editada com sucesso!')
                return redirect('website:listar_salas')
            except IntegrityError:
                messages.error(request, "Você já tem uma sala com esse nome neste pavilhão.")
    else:
        form = SalaModelForm(instance=sala, usuario=request.user)
    context = {'form': form, 'sala': sala}
    return render(request, 'criar_sala.html', context)


@login_required
def deletar_salas(request, uuid):
    sala = get_object_or_404(Sala, uuid=uuid)
    pavilhao = sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

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
def deletar_horarios(request, uuid):
    horario = get_object_or_404(Horario, uuid=uuid)
    pavilhao = horario.sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

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
def editar_horarios(request, uuid):
    horario = get_object_or_404(Horario, uuid=uuid)
    pavilhao = horario.sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

    if request.method == 'POST':
        form = HorarioModelForm(request.POST, instance=horario, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Horário editado com sucesso!')
            return redirect('website:listar_horarios')
    else:
        form = HorarioModelForm(instance=horario, usuario=request.user)
    context = {'form': form, 'horario': horario}
    return render(request, 'criar_horario.html', context)


@login_required
def deletar_pavilhoes(request, uuid):
    pavilhao = get_object_or_404(Pavilhao, uuid=uuid)

    if pavilhao.usuario != request.user:
        raise Http404

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
def editar_pavilhoes(request, uuid):
    pavilhao = get_object_or_404(Pavilhao, uuid=uuid)

    if pavilhao.usuario != request.user:
        raise Http404

    if request.method == 'POST':
        form = PavilhaoModelForm(request.POST, instance=pavilhao)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,
                                 'Pavilhão editado com sucesso!')
                return redirect('website:listar_pavilhoes')
            except IntegrityError:
                messages.error(request, "Você já tem um pavilhão com esse nome")
    else:
        form = PavilhaoModelForm(instance=pavilhao)
    context = {'form': form, 'pavilhao': pavilhao}
    return render(request, 'criar_pavilhao.html', context)


@login_required
def editar_ares(request, uuid):
    ar = get_object_or_404(ArCondicionado, uuid=uuid)
    pavilhao = ar.sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

    if request.method == 'POST':
        form = ArCondicionadoModelForm(request.POST, instance=ar, usuario=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,
                                 'Ar-condicionado editado com sucesso!')
                return redirect('website:listar_ares')
            except IntegrityError:
                messages.error(request, "Você já tem um ar-condicionado com esse nome nesta sala.")
    else:
        form = ArCondicionadoModelForm(instance=ar, usuario=request.user)
    context = {'form': form, 'ar': ar}
    return render(request, 'criar_ar.html', context)


@login_required
def deletar_ares(request, uuid):
    ar = get_object_or_404(ArCondicionado, uuid=uuid)
    pavilhao = ar.sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

    if request.method == 'POST':
        ar.delete()
        messages.success(request,
                         'Ar-condicionado deletado com sucesso!')
        return redirect('website:listar_ares')
    context = {'ar': ar}
    return render(request, 'deletar_ares.html', context)


@login_required
def ajustar_ar(request, uuid):
    ar = get_object_or_404(ArCondicionado, uuid=uuid)
    pavilhao = ar.sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

    context = {
        'ar': ar
    }

    return render(request, 'ajustar_ar.html', context)


@login_required
def ajustar_sala(request, uuid):
    sala = get_object_or_404(Sala, uuid=uuid)
    pavilhao = sala.pavilhao
    ares = ArCondicionado.objects.filter(sala=sala)
    ares_quantidade = ares.count()

    if pavilhao.usuario != request.user:
        raise Http404

    context = {
        'sala': sala,
        'ares': ares,
        'ares_quantidade': ares_quantidade
    }

    return render(request, 'ajustar_sala.html', context)


@login_required
def ajustes_ares(request, uuid):
    ar = get_object_or_404(ArCondicionado, uuid=uuid)
    sala = ar.sala
    pavilhao = sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

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

        return redirect('website:ajustar_ar', uuid=uuid)


@login_required
def ajustes_salas(request, uuid):
    sala = get_object_or_404(Sala, uuid=uuid)
    pavilhao = sala.pavilhao

    if pavilhao.usuario != request.user:
        raise Http404

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

        return redirect('website:ajustar_sala', uuid=uuid)


@login_required
def pagina_inicial(request):
    usuario = request.user

    # Buscar gráfico do usuário logado
    grafico = Grafico.objects.filter(usuario=usuario).first()
    valor_kWh = grafico.valor_kWh if grafico else 0.0

    # Obter pavilhões do usuário
    pavilhoes = list(Pavilhao.objects.filter(usuario=usuario))

    # Criar dicionário de gastos por pavilhão
    gasto_pav = {pav.nome: pav.consumo_total() * valor_kWh for pav in pavilhoes}

    # Calcular consumo total geral
    consumo_total_geral = sum(pav.consumo_total() for pav in pavilhoes)
    gasto_total_geral = consumo_total_geral * valor_kWh

    # Dados para gráfico de pizza
    dados_pizza = {pav.nome: gasto_pav.get(pav.nome, 0) for pav in pavilhoes}

    # Consumo por dia da semana
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    consumo_diario = {dia: 0 for dia in dias_semana}

    for pav in pavilhoes:
        for sala in pav.salas.all():
            for horario in sala.horarios.all():
                dias = [d.strip(" []'") for d in horario.dias_da_semana.split(",")]

                inicio = horario.horario_inicio.hour + (horario.horario_inicio.minute / 60)
                fim = horario.horario_fim.hour + (horario.horario_fim.minute / 60)

                if fim < inicio:
                    horas_uso = (24 - inicio) + fim
                else:
                    horas_uso = fim - inicio

                for ac in sala.ares_condicionados.all():
                    consumo_kWh = ac.potencia_kw * horas_uso
                    for dia in dias:
                        if dia in consumo_diario:
                            consumo_diario[dia] += consumo_kWh

    total_kWh_semana = sum(consumo_diario.values())

    dados_barras = OrderedDict((dia, consumo_diario[dia]) for dia in dias_semana)

    context = {
        "dados_pizza": json.dumps(dados_pizza),
        "dados_barras": json.dumps(dados_barras),
        "total_gasto": f'R$ {gasto_total_geral:,.2f}'.replace(',', '.'),
        "total_kWh_semana": f'{total_kWh_semana:.2f} kWh',
        "grafico": grafico
    }

    return render(request, 'pagina_inicial.html', context)


@login_required
def editar_grafico(request):
    usuario = request.user
    grafico, created = Grafico.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        form = GraficoModelForm(request.POST, instance=grafico)
        if form.is_valid():
            novo_grafico = form.save(commit=False)
            novo_grafico.usuario = usuario
            novo_grafico.save()
            return redirect('website:pagina_inicial')
    else:
        form = GraficoModelForm(instance=grafico)

    context = {
        'form': form,
        'grafico': grafico
    }
    return render(request, 'editar_grafico.html', context)
