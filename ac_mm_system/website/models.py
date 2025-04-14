import re
from datetime import datetime, timedelta

import uuid
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


class Pavilhao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField('Nome', max_length=100, unique=True)
    numero_salas = models.IntegerField('Número de salas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def consumo_total(self):
        """Calcula o consumo total do pavilhão somando o consumo de todas as salas"""
        return sum(sala.consumo_total() for sala in self.salas.all())

    def __str__(self):
        return self.nome


class Sala(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField('Nome', max_length=100, unique=True)
    pavilhao = models.ForeignKey(Pavilhao, on_delete=models.CASCADE, related_name="salas")
    topico_mqtt = models.CharField(max_length=100, editable=False)

    def total_horas_diarias(self):
        """Calcula o total de horas que a sala está em uso por dia."""
        total_horas = 0
        horarios = self.horarios.all()

        for horario in horarios:
            inicio = datetime.combine(datetime.today(), horario.horario_inicio)
            fim = datetime.combine(datetime.today(), horario.horario_fim)

            if fim < inicio:
                fim += timedelta(days=1)

            total_horas += (fim - inicio).seconds / 3600

        return total_horas

    def consumo_total(self):
        return sum(ac.consumo_mensal() for ac in self.ares_condicionados.all())

    def save(self, *args, **kwargs):
        self.nome = re.sub(r'[^a-zA-Z0-9 ]', '', self.nome)
        self.topico_mqtt = self.nome.lower().replace(" ", "_")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class ArCondicionado(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField('Nome', max_length=50)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="ares_condicionados")
    potencia_kw = models.FloatField('Potência')
    consumo = models.FloatField('Consumo')

    CONSUMO_UNIDADES = [
        ('kWh/mês', 'kWh/mês'),
        ('kWh/ano', 'kWh/ano'),
    ]
    consumo_unidade = models.CharField(max_length=10, choices=CONSUMO_UNIDADES, default='kWh/ano')

    def save(self, *args, **kwargs):
        if self.consumo_unidade == 'kWh/mês':
            self.potencia_kw = self.consumo / 30
        elif self.consumo_unidade == 'kWh/ano':
            self.potencia_kw = self.consumo / 2080

        super().save(*args, **kwargs)

    def horas_diarias(self):
        return self.sala.total_horas_diarias()

    def consumo_mensal(self):
        return self.potencia_kw * self.horas_diarias() * 30

    def __str__(self):
        return self.nome


class Horario(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    TURNOS = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
        ('Madrugada', 'Madrugada'),
    ]
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="horarios")
    dias_da_semana = models.CharField(max_length=100)
    turno = models.CharField(max_length=30, blank=True)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def clean(self):
        if self.horario_inicio == self.horario_fim:
            raise ValidationError("O horário de início e fim não podem ser iguais.")

        if Horario.objects.filter(
                sala=self.sala,
                horario_inicio=self.horario_inicio,
                horario_fim=self.horario_fim,
                dias_da_semana=self.dias_da_semana
        ).exclude(id=self.id).exists():
            raise ValidationError("Este mesmo horário já existe para esta sala.")

        dias_selecionados = {d.strip(" []'") for d in self.dias_da_semana.lower().split(",")}

        conflitos = Horario.objects.filter(sala=self.sala).exclude(id=self.id)

        for horario in conflitos:
            dias_ocupados = {d.strip(" []'") for d in horario.dias_da_semana.lower().split(",")}

            if dias_selecionados & dias_ocupados:
                conflito = False

                if self.horario_inicio < self.horario_fim:
                    if not (self.horario_fim <= horario.horario_inicio or self.horario_inicio >= horario.horario_fim):
                        conflito = True
                else:
                    if self.horario_inicio < horario.horario_fim or self.horario_fim > horario.horario_inicio:
                        conflito = True

                if conflito:
                    raise ValidationError(
                        f"Conflito de horário! A sala já possui um horário de {horario.horario_inicio} "
                        f"até {horario.horario_fim} no(s) dia(s) {horario.dias_da_semana}."
                    )

    def save(self, *args, **kwargs):
        self.clean()

        turnos = []
        inicio = self.horario_inicio.hour
        fim = self.horario_fim.hour

        if inicio > fim:
            intervalo = list(range(inicio, 24)) + list(range(0, fim + 1))
        else:
            intervalo = list(range(inicio, fim + 1))

        if len(intervalo) >= 24:
            turnos = ["Matutino", "Vespertino", "Noturno", "Madrugada"]
        else:
            turnos_map = {
                "Matutino": range(4, 12),
                "Vespertino": range(12, 18),
                "Noturno": range(18, 24),
                "Madrugada": range(0, 4)
            }

            for nome, faixa in turnos_map.items():
                if any(h in faixa for h in intervalo):
                    turnos.append(nome)

        self.turno = ", ".join(turnos)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.horario_inicio} - {self.horario_fim}'


class Grafico(models.Model):
    valor_kWh = models.FloatField('Valor em R$ por kWh', default=0.0)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'R${self.valor_kWh}'
