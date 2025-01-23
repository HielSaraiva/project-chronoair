from django import forms

from .models import Pavilhao, Horario, Sala


class PavilhaoModelForm(forms.ModelForm):
    class Meta:
        model = Pavilhao
        fields = ['nome', 'numero_salas']


DIAS_DA_SEMANA = [
    ('Segunda', 'Segunda-feira'),
    ('Terça', 'Terça-feira'),
    ('Quarta', 'Quarta-feira'),
    ('Quinta', 'Quinta-feira'),
    ('Sexta', 'Sexta-feira'),
    ('Sábado', 'Sábado'),
    ('Domingo', 'Domingo'),
]

class HorarioModelForm(forms.ModelForm):
    dias_da_semana = forms.MultipleChoiceField(choices=DIAS_DA_SEMANA, widget= forms.CheckboxSelectMultiple) # permite escolher mais de um dia da semana
    class Meta:
        model = Horario
        fields = ['pavilhao','dias_da_semana','horario_inicio','horario_fim']

class SalaModelForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome','pavilhao','horario']