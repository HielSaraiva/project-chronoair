import ssl
import json
from paho.mqtt.publish import single
from django.conf import settings  # Importa as configurações do settings.py


def mqtt_publish(topic: str, payload: dict):
    try:
        single(
            topic,
            payload=json.dumps(payload),  # Converte o payload para JSON
            hostname=settings.MQTT_BROKER,
            port=settings.MQTT_PORT,
            auth={
                "username": settings.MQTT_USERNAME,
                "password": settings.MQTT_PASSWORD,
            },
            tls={
                "ca_certs": settings.MQTT_TLS_CERT,
                "tls_version": ssl.PROTOCOL_TLSv1_2,
            }
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao publicar mensagem MQTT: {e}")