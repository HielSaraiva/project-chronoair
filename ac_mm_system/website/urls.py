from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.login, name='login'),
    path('paginaInicial/', views.pagina_inicial, name='pagina_inicial'), # pagina inicial
    path('listaPavilhoes/', views.listar_pavilhoes, name='listar_pavilhoes'), # visualização da lista com os pavilhões criados
    path('listaSalas/', views.listar_salas, name='listar_salas'), # visualização da lista com as salas criados
    path('listaAr/', views.listar_ar, name='listar_ar'), # visualização da lista com os ares criados
    path('listaHorarios/', views.listar_horarios, name='listar_horarios'), # visualização da lista com os horarios criados
    path('criarPavilhoes/', views.criar_pavilhao, name='criar_pavilhoes'), # cadastro dos pavilhões
    path('criarHorarios/', views.criar_horario, name='criar_horarios'), # cadastro dos horários
    path('criarSalas/', views.criar_sala, name='criar_salas'), # cadastro das salas
    path('editarSalas/<str:pk>/', views.editar_salas, name='editar_salas'),
    path('deletarSalas/<str:pk>/', views.deletar_salas, name='deletar_salas'),
    path('editarHorarios/<str:pk>/', views.editar_horarios, name='editar_horarios'),
    path('deletarHorarios/<str:pk>/', views.deletar_horarios, name='deletar_horarios'),
    path('deletarPavilhoes/<str:pk>/', views.deletar_pavilhoes, name='deletar_pavilhoes'),
    path('editarPavilhoes/<str:pk>/', views.editar_pavilhoes, name='editar_pavilhoes'),
]