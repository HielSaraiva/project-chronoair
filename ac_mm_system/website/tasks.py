

from django.utils import timezone
from website.mqtt import mqtt_publish
from website.models import Horario, Sala
from celery import shared_task


@shared_task
def verificar_horarios():
    # Import dentro da função evita problemas de import circular
    from website.tasks_mqtt import enviar_comando_mqtt

    agora = timezone.localtime()
    agora_hora_minuto = agora.time().replace(second=0, microsecond=0)
    dia_atual = agora.strftime('%A')

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

    horarios_inicio = Horario.objects.filter(
        horario_inicio__hour=agora_hora_minuto.hour,
        horario_inicio__minute=agora_hora_minuto.minute,
        dias_da_semana__icontains=dia_atual_pt
    )

    horarios_fim = Horario.objects.filter(
        horario_fim__hour=agora_hora_minuto.hour,
        horario_fim__minute=agora_hora_minuto.minute,
        dias_da_semana__icontains=dia_atual_pt
    )

    # Criar conjuntos para evitar conflitos
    salas_para_ligar = set(h.sala_id for h in horarios_inicio)
    salas_para_desligar = set(h.sala_id for h in horarios_fim)

    # Remover salas que estão nas duas listas (conflito no mesmo minuto)
    conflito = salas_para_ligar & salas_para_desligar
    salas_para_desligar -= conflito

    # Enviar comandos para ligar
    for sala_id in salas_para_ligar:
        sala = Sala.objects.get(pk=sala_id)
        enviar_comando_mqtt.delay(sala.topico_mqtt, {'comando': 'ligar'})

    # Enviar comandos para desligar
    for sala_id in salas_para_desligar:
        sala = Sala.objects.get(pk=sala_id)
        enviar_comando_mqtt.delay(sala.topico_mqtt, {'comando': 'desligar'})

    return horarios_inicio, horarios_fim


@shared_task
def verificar_periodo():
    from website.tasks_mqtt import enviar_comando_mqtt

    agora = timezone.localtime()
    agora_hora_minuto = agora.time().replace(second=0, microsecond=0)
    dia_atual = agora.strftime('%A')

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

    salas = Sala.objects.all()
    for sala in salas:
        if sala.ares_condicionados.exists():
            horarios_hoje = Horario.objects.filter(
                sala=sala,
                dias_da_semana__icontains=dia_atual_pt
            )

            algum_horario_ativo = any(
                # Talvez precise retirar o = do lado direito, tenho que testar -> Hiel
                h.horario_inicio <= agora_hora_minuto < h.horario_fim
                for h in horarios_hoje
            )

            if not algum_horario_ativo:
                enviar_comando_mqtt.delay(
                    sala.topico_mqtt, {'comando': 'desligar'})
