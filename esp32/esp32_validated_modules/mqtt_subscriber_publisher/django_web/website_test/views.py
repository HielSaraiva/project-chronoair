from django.shortcuts import render
from .mqtt import mqtt_publish  # Importa a função do mqtt.py


def index(request):
    if request.method == "POST":
        acao = request.POST.get("acao")  # Pega o valor do botão clicado
        try:
            if acao == "gravarOff":
                # Publica no tópico "comando/gravarOff"
                mqtt_publish("comando", {"acao": "gravarOff"})
                return render(request, "index.html", {"mensagem": "Comando 'gravarOff' enviado com sucesso!"})

            elif acao == "emitirOff":
                # Publica no tópico "comando/emitirOff"
                mqtt_publish("comando", {"acao": "emitirOff"})
                return render(request, "index.html", {"mensagem": "Comando 'emitirOff' enviado com sucesso!"})

            elif acao == "gravarOn":
                # Publica no tópico "comando/gravarOn"
                mqtt_publish("comando", {"acao": "gravarOn"})
                return render(request, "index.html", {"mensagem": "Comando 'gravarOn' enviado com sucesso!"})
            
            elif acao == "emitirOn":
                # Publica no tópico "comando/emitirOn"
                mqtt_publish("comando", {"acao": "emitirOn"})
                return render(request, "index.html", {"mensagem": "Comando 'emitirOn' enviado com sucesso!"})
            
            else:
                return render(request, "index.html", {"erro": "Ação inválida enviada!"})

        except Exception as e:
            # Renderiza um erro genérico se houver problemas com a publicação
            return render(request, "index.html", {"erro": f"Erro ao enviar comando: {str(e)}"})

    # Método GET: carrega a página inicial
    return render(request, "index.html")
