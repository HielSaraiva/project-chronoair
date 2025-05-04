import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower

from .models import Pavilhao, Horario, Sala, ArCondicionado, Grafico

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

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        usuario = self.usuario  # Obtém o usuário da inicialização do formulário

        if nome and usuario:
            if Pavilhao.objects.filter(usuario=usuario, nome=nome).exists():
                self.add_error('nome', ValidationError(
                    ("Você já tem um pavilhão com este nome."),
                    code='unique_together'
                ))
        return cleaned_data

    def clean_numero_salas(self):
        numero_salas = self.cleaned_data.get('numero_salas')

        # Certifica-se de que estamos na edição de um objeto existente no banco de dados
        if self.instance and self.instance.pk:
            numero_salas_existente = self.instance.salas.count()

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

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['pavilhao'].queryset = Pavilhao.objects.filter(
                usuario=usuario).order_by(Lower('nome'))

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        pavilhao = cleaned_data.get('pavilhao')

        if nome and pavilhao:
            if Sala.objects.filter(pavilhao=pavilhao, nome=nome).exists():
                self.add_error('nome', ValidationError(
                    ("Já existe uma sala com este nome neste pavilhão."),
                    code='unique_together'
                ))
        return cleaned_data

    def clean_pavilhao(self):
        pavilhao = self.cleaned_data.get('pavilhao')

        if pavilhao:
            # Exclui a sala atual da contagem se estiver em edição
            salas_existentes = pavilhao.salas.all()
            if self.instance.pk:
                salas_existentes = salas_existentes.exclude(
                    pk=self.instance.pk)
            if salas_existentes.count() >= pavilhao.numero_salas:
                raise ValidationError(
                    f"O pavilhão '{pavilhao.nome}' já atingiu o número máximo de salas permitido ({pavilhao.numero_salas})."
                )
        return pavilhao

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")

        if not re.match(r'^[a-zA-Z0-9 ]+$', nome):
            raise forms.ValidationError(
                "O nome da sala só pode conter letras, números e espaços.")
        return nome

    def save(self, commit=True):
        sala = super().save(commit=False)
        # Remove caracteres especiais
        sala.nome = re.sub(r'[^a-zA-Z0-9 ]', '', sala.nome)
        sala.topico_mqtt = sala.nome.lower().replace(" ", "_")  # Formata o tópico MQTT

        if commit:
            sala.save()
        return sala


# Formulário para o modelo ArCondicionado
class ArCondicionadoModelForm(forms.ModelForm):
    class Meta:
        model = ArCondicionado
        fields = [
            'nome',
            'sala',
            'consumo',
            'consumo_unidade'
        ]
        labels = {
            'nome': 'Ar-condicionado',
            'consumo': 'Consumo'
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'consumo': forms.NumberInput(attrs={'placeholder': '(kWh/mês ou kWh/ano)', 'min': 0.1}),
            'consumo_unidade': forms.Select(attrs={'placeholder': 'Unidade'}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['sala'].queryset = Sala.objects.filter(
                pavilhao__usuario=usuario).order_by(Lower('nome'))

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        sala = cleaned_data.get('sala')

        if nome and sala:
            if ArCondicionado.objects.filter(sala=sala, nome=nome).exists():
                self.add_error('nome', ValidationError(
                    ("Já existe um ar-condicionado com este nome nesta sala."),
                    code='unique_together'
                ))
        return cleaned_data

    def clean_sala(self):
        sala = self.cleaned_data.get('sala')
        if sala:
            # Exclui o ar-condicionado atual da contagem se estiver em edição
            ares_existentes = sala.ares_condicionados.all()
            if self.instance.pk:
                ares_existentes = ares_existentes.exclude(pk=self.instance.pk)
            if ares_existentes.count() >= 3:
                raise ValidationError(
                    "Já existem 3 ar-condicionados registrados para esta sala.")
        return sala

# Formulário para o modelo Horario


class HorarioModelForm(forms.ModelForm):
    pavilhao = forms.ModelChoiceField(
        queryset=Pavilhao.objects.all(),
        required=False,
        label="Pavilhão",
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )

    dias_da_semana = forms.MultipleChoiceField(
        choices=DIAS_DA_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        label="Dias da Semana"
    )

    class Meta:
        model = Horario
        fields = [
            'sala',
            'dias_da_semana',
            'horario_inicio',
            'horario_fim',
        ]
        labels = {
            'sala': 'Sala',
            'horario_inicio': 'Horário de Início',
            'horario_fim': 'Horário de Término',
        }
        widgets = {
            'horario_inicio': forms.TextInput(attrs={'type': 'time', 'placeholder': 'HH:mm'}),
            'horario_fim': forms.TextInput(attrs={'type': 'time', 'placeholder': 'HH:mm'}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        pavilhao_id = self.data.get('pavilhao') or self.initial.get('pavilhao')

        # Caso não tenha pavilhao, faça a consulta de salas vazia (sem opções)
        if pavilhao_id:
            try:
                pavilhao_id = int(pavilhao_id)
                salas = Sala.objects.filter(pavilhao_id=pavilhao_id)
                if usuario:
                    salas = salas.filter(pavilhao__usuario=usuario)
                self.fields['sala'].queryset = salas.order_by(Lower('nome'))
                self.initial['pavilhao'] = pavilhao_id
                self.fields['pavilhao'].initial = pavilhao_id
            except (ValueError, TypeError):
                self.fields['sala'].queryset = Sala.objects.none()
        # Quando for edição, se a sala já estiver associada ao horário
        elif self.instance.pk and self.instance.sala:
            salas = Sala.objects.filter(pavilhao=self.instance.sala.pavilhao)
            if usuario:
                salas = salas.filter(pavilhao__usuario=usuario)
            self.fields['sala'].queryset = salas.order_by(Lower('nome'))
            self.initial['pavilhao'] = self.instance.sala.pavilhao.id
            self.fields['pavilhao'].initial = self.instance.sala.pavilhao

        # Define os dias da semana pré-selecionados na edição
        if self.instance and self.instance.pk:
            self.initial['dias_da_semana'] = self.instance.dias_da_semana.split(
                ",") if self.instance.dias_da_semana else []

    def clean_dias_da_semana(self):
        dias = self.cleaned_data.get('dias_da_semana', [])
        return ",".join(dias)

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        if not sala:
            self.add_error('sala', 'Você deve selecionar uma sala.')
        return cleaned_data


class GraficoModelForm(forms.ModelForm):
    class Meta:
        model = Grafico
        fields = ['valor_kWh']
        labels = {
            'valor_kWh': 'Valor em R$ por kWh',
        }
        widgets = {
            'valor_kWh': forms.NumberInput(attrs={'placeholder': 'Valor em R$ por kWh'}),
        }

    def clean_valor_kWh(self):
        valor_kWh = self.cleaned_data.get('valor_kWh')
        if valor_kWh is None or valor_kWh < 0.0:
            raise forms.ValidationError(
                "O valor deve ser um número maior ou igual a 0.")
        return valor_kWh
