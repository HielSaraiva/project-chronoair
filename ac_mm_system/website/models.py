import re

from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
from django.db.models import ForeignKey


class Pavilhao(models.Model):
    # Atributos
    nome = models.CharField('Nome', max_length=100, unique=True)
    numero_salas = models.IntegerField('Numero de salas')

    def __str__(self):  # Define a representação em texto do objeto
        return self.nome


class Sala(models.Model):
    # Atributos
    nome = models.CharField('Nome', max_length=100, unique=True)
    pavilhao = ForeignKey(Pavilhao, on_delete=models.CASCADE)
    topico_mqtt = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        # Remove caracteres especiais, exceto letras, números e espaços
        self.nome = re.sub(r'[^a-zA-Z0-9 ]', '', self.nome)
        # Gera o tópico MQTT substituindo espaços por _
        self.topico_mqtt = self.nome.lower().replace(" ", "_")

        super().save(*args, **kwargs)  # Salva o modelo normalmente

    def __str__(self):  # Define a representação em texto do objeto
        return self.nome


class ArCondicionado(models.Model):
    # Atributos
    nome = models.CharField('Nome', max_length=50, unique=False)
    sala = ForeignKey(Sala, on_delete=models.CASCADE)
    potencia = models.IntegerField('Potência')

    def __str__(self):  # Define a representação em texto do objeto
        return self.nome


class Horario(models.Model):
    # Atributos
    pavilhao = ForeignKey(Pavilhao, on_delete=models.CASCADE)
    sala = ForeignKey(Sala, on_delete=models.CASCADE)
    dias_da_semana = models.CharField(max_length=100)
    turno = models.CharField(max_length=100)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):  # Define a representação em texto do objeto
        return f'{self.horario_inicio} - {self.horario_fim}'
