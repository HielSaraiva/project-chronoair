from django.db import models

# Create your models here.
from django.db.models import ForeignKey




class Pavilhao(models.Model):
    # Atributos
    nome = models.CharField('Nome', max_length=100)
    numero_salas = models.IntegerField('Numero de salas')

    def __str__(self): # Define a representação em texto do objeto
            return self.nome


class Horario(models.Model):
    # Atributos
    pavilhao = ForeignKey(Pavilhao, on_delete=models.CASCADE)
    dias_da_semana = models.CharField(max_length=100)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self): # Define a representação em texto do objeto
        return f'{self.horario_inicio} - {self.horario_fim}'


class Sala(models.Model):
    # Atributos
    nome = models.CharField('Nome', max_length=100)
    pavilhao = ForeignKey(Pavilhao, on_delete=models.CASCADE)
    horario = ForeignKey(Horario, on_delete=models.CASCADE, related_name='sala_horario', default=1)

    def __str__(self): # Define a representação em texto do objeto
        return self.nome
