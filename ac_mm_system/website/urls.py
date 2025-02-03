from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'website'
urlpatterns = [
    # url raiz
    path('', RedirectView.as_view(url='/pagina_inicial/'), name='raiz'),

    # pagina inicial
    path('pagina_inicial/', views.pagina_inicial, name='pagina_inicial'),

    # Lista de pavilhões
    path('listar_pavilhoes/', views.listar_pavilhoes, name='listar_pavilhoes'),

    # Lista de salas
    path('listar_salas/', views.listar_salas, name='listar_salas'),

    # Lista de ares-condicionados
    path('listar_ares/', views.listar_ares, name='listar_ares'),

    # Lista de horários
    path('listar_horarios/', views.listar_horarios, name='listar_horarios'),

    # Cadastro de pavilhão
    path('criar_pavilhao/', views.criar_pavilhao, name='criar_pavilhao'),

    # Cadastro de horário
    path('criar_horario/', views.criar_horario, name='criar_horario'),

    # Cadastro de sala
    path('criar_sala/', views.criar_sala, name='criar_sala'),

    # Editar sala
    path('editar_salas/<str:pk>/', views.editar_salas, name='editar_salas'),

    # Editar pavilhão
    path('editar_pavilhoes/<str:pk>/', views.editar_pavilhoes, name='editar_pavilhoes'),

    # Editar horário
    path('editar_horarios/<str:pk>/', views.editar_horarios, name='editar_horarios'),

    # Deletar sala
    path('deletar_salas/<str:pk>/', views.deletar_salas, name='deletar_salas'),

    # Deletar horário
    path('deletar_horarios/<str:pk>/', views.deletar_horarios, name='deletar_horarios'),

    # Deletar pavilhão
    path('deletar_pavilhoes/<str:pk>/', views.deletar_pavilhoes, name='deletar_pavilhoes'),
]