import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Pavilhao, Horario, Sala, ArCondicionado

# Constante para os dias da semana
DIAS_DA_SEMANA = [
    ('Segunda', 'Segunda-feira'),
    ('Terça', 'Terça-feira'),
    ('Quarta', 'Quarta-feira'),
    ('Quinta', 'Quinta-feira'),
    ('Sexta', 'Sexta-feira'),
    ('Sábado', 'Sábado'),
    ('Domingo', 'Domingo'),
]

TURNOS = [
    ('Matutino', 'Matutino'),
    ('Vespertino', 'Vespertino'),
    ('Noturno', 'Noturno'),
]


# Formulário para o modelo Pavilhao
class PavilhaoModelForm(forms.ModelForm):
    class Meta:
        model = Pavilhao
        fields = [
            'nome',
            'numero_salas',
        ]
        labels = {
            'nome': 'Pavilhão',
            'numero_salas': 'Número de Salas',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'numero_salas': forms.NumberInput(attrs={'placeholder': 'Número', 'min': 1}),
        }

    def clean_numero_salas(self):
        numero_salas = self.cleaned_data.get('numero_salas')

        if self.instance and self.instance.pk:  # Certifica-se de que estamos na edição de um objeto existente no banco de dados
            numero_salas_existente = self.instance.sala_set.count()

            if numero_salas < numero_salas_existente:
                raise ValidationError(
                    f"O número de salas não pode ser reduzido para abaixo de {numero_salas_existente}, pois já existem salas cadastradas no pavilhão."
                )

        return numero_salas


# Formulário para o modelo Sala
class SalaModelForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = [
            'nome',
            'pavilhao',
        ]
        labels = {
            'nome': 'Sala',
            'pavilhao': 'Pavilhão',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
        }

    def clean_pavilhao(self):
        pavilhao = self.cleaned_data.get('pavilhao')

        if pavilhao:
            # Contar o número de salas existentes no pavilhão
            numero_salas_existentes = pavilhao.sala_set.count()
            numero_salas_maximo = pavilhao.numero_salas

            # Verificar se o número máximo foi atingido
            if numero_salas_existentes >= numero_salas_maximo:
                raise ValidationError(
                    f"O pavilhão '{pavilhao.nome}' já atingiu o número máximo de salas permitido ({numero_salas_maximo})."
                )

        return pavilhao


# Formulário para o modelo ArCondicionado
class ArCondicionadoModelForm(forms.ModelForm):
    class Meta:
        model = ArCondicionado
        fields = [
            'nome',
            'sala',
            'topico_mqtt',
        ]
        labels = {
            'nome': 'Ar-condicionado',
            'topico_mqtt': 'Tópico MQTT',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'topico_mqtt': forms.TextInput(attrs={'placeholder': 'Nome'})
        }

    def clean_topico_mqtt(self):
        topico = self.cleaned_data.get('topico_mqtt')

        # Verifica se o tópico contém apenas letras minúsculas e números
        if not re.match(r'^[a-z0-9]+$', topico):
            raise ValidationError(
                "O tópico MQTT deve conter apenas letras minúsculas e números, sem espaços e sem caracteres especiais.")

        return topico

    def clean_sala(self):
        sala = self.cleaned_data.get('sala')

        # Contar quantos ar-condicionados já estão associados à sala
        if ArCondicionado.objects.filter(sala=sala).count() >= 3:
            raise forms.ValidationError("Já existem 3 ar-condicionados registrados para esta sala.")

        return sala


# Formulário para o modelo Horario
class HorarioModelForm(forms.ModelForm):
    dias_da_semana = forms.MultipleChoiceField(
        choices=DIAS_DA_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        label="Dias da Semana"
    )  # Permite escolher mais de um dia da semana

    turno = forms.ChoiceField(
        choices=TURNOS,
        widget=forms.RadioSelect,
        label="Turno"
    )

    class Meta:
        model = Horario
        fields = [
            'pavilhao',
            'sala',
            'turno',
            'dias_da_semana',
            'horario_inicio',
            'horario_fim',
        ]
        labels = {
            'pavilhao': 'Pavilhão',
            'sala': 'Sala',
            'turno': 'Turno',
            'horario_inicio': 'Horário de Início',
            'horario_fim': 'Horário de Término',
        }
        widgets = {
            'horario_inicio': forms.TextInput(attrs={'type': 'time', 'placeholder': 'HH:mm'}),
            'horario_fim': forms.TextInput(attrs={'type': 'time', 'placeholder': 'HH:mm'}),
        }
