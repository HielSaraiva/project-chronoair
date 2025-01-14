# Validando módulo mqtt-web-esp32

## Atualizando pip

````````
python.exe -m pip install --upgrade pip
````````

## Baixando bibliotecas

````````
pip install django mysqlclient gunicorn django-bootstrap5 paho-mqtt
````````

## Configurar o banco de dados MySQL

````````
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_web',
        'USER': 'developer',
        'PASSWORD': '1234567',
        'HOST': 'localhost',  # Ou o IP do servidor MySQL
        'PORT': '3306',  # Porta padrão do MySQL
    }
}
````````

- Lembre-se de criar um banco de dados na sua máquina de mesmo nome

## Adicionar as aplicações ao settings.py

````````
INSTALLED_APPS = [
    # Minhas aplicacoes
    'website_test',

    # Aplicacoes de terceiros
    'django_bootstrap5',
    ...
````````

## Inicializar banco de dados

````````
python manage.py migrate
````````

## Visualizando o Projeto a primeira vez

````````
python manage.py runserver
````````

## Criando um superusuario

````````
python manage.py createsuperuser
````````

- admin
- hiel1234

## Mapeando a url da aplicacao na pasta do projeto / urls.py

````````
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website_test.urls')),
]
````````

## Criando o arquivo urls.py na pasta da aplicacao

````````
from django.urls import path

from . import views

app_name = "website_test"
urlpatterns = [
    # Página inicial
    path("", views.index, name="index"),
]
````````