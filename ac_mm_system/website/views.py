# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import PavilhaoModelForm, HorarioModelForm, SalaModelForm, ArCondicionadoModelForm, GraficoModelForm
from .models import Pavilhao, Horario, Sala, ArCondicionado, Grafico
from .mqtt import mqtt_publish

from collections import OrderedDict
import json
from chartjs.views.lines import BaseLineChartView


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
            salas = Sala.objects.filter(pavilhao__uuid=filtrarpavilhao)
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
        ares = ares.filter(sala__pavilhao__uuid=filtrarpavilhao)
        salas = salas.filter(pavilhao__uuid=filtrarpavilhao)  # Atualiza as salas conforme o pavilhão
    if filtrarsala:
        ares = ares.filter(sala__uuid=filtrarsala)

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
def editar_salas(request, uuid):
    sala = Sala.objects.get(uuid=uuid)

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
def deletar_salas(request, uuid):
    sala = Sala.objects.get(uuid=uuid)
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
    horario = Horario.objects.get(uuid=uuid)
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
    horario = Horario.objects.get(uuid=uuid)

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
def deletar_pavilhoes(request, uuid):
    pavilhao = Pavilhao.objects.get(uuid=uuid)
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
    pavilhao = Pavilhao.objects.get(uuid=uuid)

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
def editar_ares(request, uuid):
    ar = ArCondicionado.objects.get(uuid=uuid)

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
def deletar_ares(request, uuid):
    ar = ArCondicionado.objects.get(uuid=uuid)

    if request.method == 'POST':
        ar.delete()
        messages.success(request,
                         'Ar-condicionado deletado com sucesso!')
        return redirect('website:listar_ares')
    context = {'ar': ar}
    return render(request, 'deletar_ares.html', context)


@login_required
def ajustar_ar(request, uuid):
    ar = ArCondicionado.objects.get(uuid=uuid)

    context = {
        'ar': ar
    }

    return render(request, 'ajustar_ar.html', context)


@login_required
def ajustar_sala(request, uuid):
    sala = Sala.objects.get(uuid=uuid)
    ares = ArCondicionado.objects.filter(sala=sala)
    ares_quantidade = ares.count()

    context = {
        'sala': sala,
        'ares': ares,
        'ares_quantidade': ares_quantidade
    }

    return render(request, 'ajustar_sala.html', context)


@login_required
def ajustes_ares(request, uuid):
    ar = ArCondicionado.objects.get(uuid=uuid)  # Obtém o ar-condicionado atualizado
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

        return redirect('website:ajustar_ar', uuid=uuid)


@login_required
def ajustes_salas(request, uuid):
    sala = Sala.objects.get(uuid=uuid)  # Obtém a sala

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
    # Buscar o primeiro objeto Grafico ou definir valor padrão
    grafico = Grafico.objects.first()
    valor_kWh = grafico.valor_kWh if grafico else 0.0

    # Obter todos os pavilhões
    pavilhoes = list(Pavilhao.objects.all())

    # Criar dicionário de gastos por pavilhão
    gasto_pav = {pav.nome: pav.consumo_total() * valor_kWh for pav in pavilhoes}

    # Calcular consumo total geral
    consumo_total_geral = sum(pav.consumo_total() for pav in pavilhoes)
    gasto_total_geral = consumo_total_geral * valor_kWh

    # Criar dicionário de dados do gráfico de pizza
    dados_pizza = {pav.nome: gasto_pav.get(pav.nome, 0) for pav in pavilhoes}

    # Calcular consumo por dia da semana
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    consumo_diario = {dia: 0 for dia in dias_semana}

    for pav in pavilhoes:
        for sala in pav.salas.all():
            for horario in sala.horarios.all():
                dias = [d.strip(" []'") for d in horario.dias_da_semana.split(",")]

                # Calcular o tempo de funcionamento diário em horas
                inicio = horario.horario_inicio.hour + (horario.horario_inicio.minute / 60)
                fim = horario.horario_fim.hour + (horario.horario_fim.minute / 60)

                if fim < inicio:  # Caso o horário passe da meia-noite
                    horas_uso = (24 - inicio) + fim
                else:
                    horas_uso = fim - inicio

                # Somar consumo de cada ar-condicionado da sala
                for ac in sala.ares_condicionados.all():
                    consumo_kWh = ac.potencia_kw * horas_uso  # Consumo diário desse AC
                    for dia in dias:
                        if dia in consumo_diario:
                            consumo_diario[dia] += consumo_kWh

    # Calcular o total da semana
    total_kWh_semana = sum(consumo_diario.values())

    # Criar dicionário de dados para o gráfico de barras
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
    grafico = Grafico.objects.first()
    if request.method == 'POST':
        form = GraficoModelForm(request.POST, instance=grafico)
        if form.is_valid():
            form.save()
            return redirect('website:pagina_inicial')
    else:
        form = GraficoModelForm(instance=grafico)
    context = {
        'form': form,
        'grafico': grafico
    }
    return render(request, 'editar_grafico.html', context)