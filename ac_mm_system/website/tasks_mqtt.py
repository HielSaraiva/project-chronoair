from celery import shared_task
from website.mqtt import mqtt_publish


@shared_task(bind=True)
def enviar_comando_mqtt(self, topico, payload):
    try:
        mqtt_publish(topico, payload)
        print(f"[MQTT] Enviado para {topico}: {payload}")
    except Exception as e:
        print(f"[MQTT] Falha ao enviar para {topico}. Tentando novamente...")
        raise self.retry(exc=e)
