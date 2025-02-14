import re

from django.core.validators import RegexValidator
from django.db import models
from django.core.exceptions import ValidationError

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
        """Fonte: https://agenciabrasil.ebc.com.br/economia/noticia/2023-01/aparelhos-de-ar-condicionado-mudam-forma-de-medir-consumo-de-energia"""
        if self.consumo_unidade == 'kWh/mês': # Mensal
            self.potencia_kw = self.consumo / 30  # Calculando a potencia (obedecendo à antiga norma = 30h/mes)
        elif self.consumo_unidade == 'kWh/ano': # Anual
            self.potencia_kw = self.consumo / 2080  # Calculando a potencia (obedecendo à nova norma = 2080h/ano)

        super().save(*args, **kwargs)

    def __str__(self):  # Define a representação em texto do objeto
        return self.nome


class Horario(models.Model):
    # Atributos
    TURNOS = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
        ('Sembrol', 'Sembrol'),
    ]
    pavilhao = ForeignKey(Pavilhao, on_delete=models.CASCADE)
    sala = ForeignKey(Sala, on_delete=models.CASCADE)
    dias_da_semana = models.CharField(max_length=100)
    turno = models.CharField(max_length=30, blank=True)  # Pode armazenar múltiplos turnos
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def clean(self):
        if self.horario_inicio == self.horario_fim:
            raise ValidationError("O horário de início e fim não podem ser iguais.") # Impede a criação de horários iguais

        if Horario.objects.filter( #Impede a criação de horários repetidos
                sala=self.sala,
                horario_inicio=self.horario_inicio,
                horario_fim=self.horario_fim,
                dias_da_semana=self.dias_da_semana
        ).exclude(id=self.id).exists():
            raise ValidationError("Este mesmo horário já existe para esta sala.")

        dias_selecionados = set(d.strip(" []'") for d in self.dias_da_semana.lower().split(",")) # Converte a string de dias (self.dias_da_semana) em um conjunto (set)

        conflitos = Horario.objects.filter(sala=self.sala).exclude(id=self.id) # Busca todos os horários da mesma sala

        for horario in conflitos: # Faz verificação com cada horário ja criado na sala
            dias_ocupados = set(d.strip(" []'") for d in horario.dias_da_semana.lower().split(","))

            if dias_selecionados & dias_ocupados: # Se os dias selecionados já tiverem horários criados, fará a verificação
                conflito = False

                if self.horario_inicio < self.horario_fim: # Se o horário não virar a noite
                    if not (self.horario_fim <= horario.horario_inicio or self.horario_inicio >= horario.horario_fim):
                        conflito = True
                else: # Se o horário virar a noite
                    if (self.horario_inicio < horario.horario_fim or self.horario_fim > horario.horario_inicio):
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

        # Caso o horário vire o dia. Ex: 22h - 03h
        if inicio > fim:
            intervalo = list(range(inicio, 24)) + list(range(0, fim + 1))
        else:
            intervalo = list(range(inicio, fim + 1))

        # Se o intervalo do horário for igual a 24, o horário automaticamente já tem todos os turnos
        if len(intervalo) >= 24:
            turnos = ["Matutino", "Vespertino", "Noturno", "Sembrol"]
        else:
            # Mapeamento dos turnos
            turnos_map = {
                "Matutino": range(4, 12),
                "Vespertino": range(12, 18),
                "Noturno": range(18, 24),
                "Sembrol": range(0, 4)
            }

            # Verifica quais turnos estão no intervalo
            for nome, faixa in turnos_map.items():
                if any(h in faixa for h in intervalo):
                    turnos.append(nome)

        self.turno = ", ".join(turnos)  # Salva os turnos em string

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.horario_inicio} - {self.horario_fim}'
