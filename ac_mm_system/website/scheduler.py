from datetime import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from website.models import Horario, Sala
from website.mqtt import mqtt_publish
from django.utils import timezone


def verificar_horarios():
    agora = timezone.localtime()
    agora_hora_minuto = agora.time().replace(second=0, microsecond=0)  # Removendo segundos e milissegundos
    dia_atual = agora.strftime('%A')  # Obtém o dia da semana em inglês (Monday, Tuesday, ...)

    # Mapeamento para o formato salvo no banco de dados
    traducao_dias = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    dia_atual_pt = traducao_dias[dia_atual]  # Converte para português

    # Filtra os horários que precisam ligar ou desligar o ar-condicionado
    horarios_inicio = Horario.objects.filter(
        horario_inicio__hour=agora_hora_minuto.hour,
        horario_inicio__minute=agora_hora_minuto.minute,
    ).filter(dias_da_semana__icontains=dia_atual_pt)  # Verifica se o dia está incluído na string

    horarios_fim = Horario.objects.filter(
        horario_fim__hour=agora_hora_minuto.hour,
        horario_fim__minute=agora_hora_minuto.minute,
    ).filter(dias_da_semana__icontains=dia_atual_pt)  # Mesma lógica para desligar

    for horario in horarios_inicio:
        topico = horario.sala.topico_mqtt
        payload = {'comando': 'ligar'}
        mqtt_publish(topico, payload)

    for horario in horarios_fim:
        topico = horario.sala.topico_mqtt
        payload = {'comando': 'desligar'}
        mqtt_publish(topico, payload)


def verificar_periodo():
    agora = timezone.localtime()
    agora_hora_minuto = agora.time().replace(second=0, microsecond=0)  # Removendo segundos e milissegundos
    dia_atual = agora.strftime('%A')  # Obtém o dia da semana em inglês (Monday, Tuesday, ...)

    # Mapeamento para o formato salvo no banco de dados
    traducao_dias = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    dia_atual_pt = traducao_dias[dia_atual]

    # Verifica todas as salas cadastradas
    salas = Sala.objects.all()
    for sala in salas:
        if sala.ares_condicionados.exists():
            horarios = Horario.objects.filter(sala=sala).filter(dias_da_semana__icontains=dia_atual_pt)
            for horario in horarios:
                if not (horario.horario_inicio <= agora_hora_minuto <= horario.horario_fim):
                    topico = sala.topico_mqtt
                    payload = {'comando': 'desligar'}
                    mqtt_publish(topico, payload)


def iniciar_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(verificar_horarios, 'interval', minutes=1)  # Executa a cada 1 minuto

    scheduler.add_job(verificar_periodo, CronTrigger(minute='0,30', hour='6-21')) # Horário comercial (6h-21h59)

    scheduler.add_job(verificar_periodo, CronTrigger(minute=0, hour='22-23,0-5')) # Período noturno (22h-5h59)

    scheduler.start()
