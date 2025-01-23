from django.urls import path, include
from .views import logIn_View, paginaInicial_View, listaPavilhoes_View, listaSalas_View, listaAr_View, \
    listaHorarios_View, listaUsuarios_View, criarPavilhao_View, criarHorario_View, criarSala_View



urlpatterns = [
    path('', logIn_View, name='login'),
    path('paginaInicial/', paginaInicial_View, name='paginainicial'), # pagina inicial
    path('listaPavilhoes/', listaPavilhoes_View, name='listapavilhoes'), # visualização da lista com os pavilhões criados
    path('listaSalas/', listaSalas_View, name='listasalas'), # visualização da lista com as salas criados
    path('listaAr/', listaAr_View, name='listaar'), # visualização da lista com os ares criados
    path('listaHorarios/', listaHorarios_View, name='listahorarios'), # visualização da lista com os horarios criados
    path('listaUsuarios/', listaUsuarios_View, name='listausuarios'), # visualização da lista com os usuários criados
    path('criarPavilhoes/', criarPavilhao_View, name='criarpavilhoes'), # cadastro dos pavilhões
    path('criarHorarios/', criarHorario_View, name='criarhorarios'), # cadastro dos horários
    path('criarSalas/', criarSala_View, name='criarsalas'), # cadastro das salas
]