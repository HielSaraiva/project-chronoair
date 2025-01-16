from django.shortcuts import render
from .mqtt import mqtt_publish  # Importa a função do mqtt.py


def index(request):
    if request.method == "POST":
        acao = request.POST.get("acao")  # Pega o valor do botão clicado
        try:
            if acao == "gravar":
                # Publica no tópico "comando/gravar"
                mqtt_publish("comando", {"acao": "gravar"})
                return render(request, "index.html", {"mensagem": "Comando 'gravar' enviado com sucesso!"})

            elif acao == "emitir":
                # Publica no tópico "comando/emitir"
                mqtt_publish("comando", {"acao": "emitir"})
                return render(request, "index.html", {"mensagem": "Comando 'emitir' enviado com sucesso!"})

            else:
                return render(request, "index.html", {"erro": "Ação inválida enviada!"})

        except Exception as e:
            # Renderiza um erro genérico se houver problemas com a publicação
            return render(request, "index.html", {"erro": f"Erro ao enviar comando: {str(e)}"})

    # Método GET: carrega a página inicial
    return render(request, "index.html")
