import ssl
import json
import paho.mqtt.publish as publish
from django.shortcuts import render
from django.conf import settings  # Importa as configurações do settings.py


def index(request):
    if request.method == "POST":
        acao = request.POST.get("acao")  # Pega o valor do botão clicado
        try:
            if acao == "gravar":
                # Publica no tópico "comando/gravar"
                publish.single(
                    "comando",
                    json.dumps({"acao": "gravar"}),  # Payload no formato JSON
                    hostname=settings.MQTT_BROKER,
                    port=settings.MQTT_PORT,
                    auth={
                        "username": settings.MQTT_USERNAME,
                        "password": settings.MQTT_PASSWORD
                    },
                    tls={
                        "ca_certs": settings.MQTT_TLS_CERT,
                        "tls_version": ssl.PROTOCOL_TLSv1_2
                    }
                )
                return render(request, "index.html", {"mensagem": "Comando 'gravar' enviado com sucesso!"})
            elif acao == "emitir":
                # Publica no tópico "comando/emitir"
                publish.single(
                    "comando",
                    json.dumps({"acao": "emitir"}),  # Payload no formato JSON
                    hostname=settings.MQTT_BROKER,
                    port=settings.MQTT_PORT,
                    auth={
                        "username": settings.MQTT_USERNAME,
                        "password": settings.MQTT_PASSWORD
                    },
                    tls={
                        "ca_certs": settings.MQTT_TLS_CERT,
                        "tls_version": ssl.PROTOCOL_TLSv1_2
                    }
                )
                return render(request, "index.html", {"mensagem": "Comando 'emitir' enviado com sucesso!"})
            else:
                return render(request, "index.html", {"erro": "Ação inválida enviada!"})
        except Exception as e:
            return render(request, "index.html", {"erro": f"Erro ao enviar comando: {str(e)}"})

    # Método GET: carrega a página inicial
    return render(request, "index.html")
