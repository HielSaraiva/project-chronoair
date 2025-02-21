from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



# Formulário customizado para o cadastro de usuários
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        # Recupera o email informado pelo usuário no formulário
        email = self.cleaned_data.get('email')

        # Verifica se já existe um usuário com o mesmo email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso. Por favor, escolha outro email.")

        return email

    def clean_username(self):
        # Recupera o nome de usuário informado pelo usuário no formulário
        username = self.cleaned_data.get('username')

        # Verifica se já existe um usuário com o mesmo username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso. Escolha outro nome de usuário.")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

