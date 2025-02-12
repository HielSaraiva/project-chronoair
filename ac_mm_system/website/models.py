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
    potencia_kw = models.FloatField('Potência', max_length=20)
    consumo = models.FloatField('Consumo', max_length=20)

    CONSUMO_UNIDADES = [
        ('kWh/mês', 'kWh/mês'),
        ('kWh/ano', 'kWh/ano'),
    ]
    consumo_unidade = models.CharField(max_length=10, choices=CONSUMO_UNIDADES, default='kWh/ano')

    def save(self, *args, **kwargs):
        if self.consumo_unidade == 'kWh/mês': # Mensal
            self.potencia_kw = self.consumo / 30  # Calculando a potencia (obedecendo à antiga norma = 30h/mes)
        elif self.consumo_unidade == 'kWh/ano': # Anual
            self.potencia_kw = self.consumo / 2080  # Calculando a potencia (obedecendo à nova norma = 2080h/ano)

        super().save(*args, **kwargs)

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
