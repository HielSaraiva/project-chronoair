from django.urls import path, include
from .views import logIn_View, paginaInicial_View, listaPavilhoes_View, listaSalas_View, listaAr_View, \
    listaHorarios_View, criarPavilhao_View, criarHorario_View, criarSala_View, editarSalas_View, deletarSalas_View, \
    deletarHorarios_View, editarHorarios_View, deletarPavilhoes_View, editarPavilhoes_View

urlpatterns = [
    path('', logIn_View, name='login'),
    path('paginaInicial/', paginaInicial_View, name='paginainicial'), # pagina inicial
    path('listaPavilhoes/', listaPavilhoes_View, name='listapavilhoes'), # visualização da lista com os pavilhões criados
    path('listaSalas/', listaSalas_View, name='listasalas'), # visualização da lista com as salas criados
    path('listaAr/', listaAr_View, name='listaar'), # visualização da lista com os ares criados
    path('listaHorarios/', listaHorarios_View, name='listahorarios'), # visualização da lista com os horarios criados
    path('criarPavilhoes/', criarPavilhao_View, name='criarpavilhoes'), # cadastro dos pavilhões
    path('criarHorarios/', criarHorario_View, name='criarhorarios'), # cadastro dos horários
    path('criarSalas/', criarSala_View, name='criarsalas'), # cadastro das salas
    path('editarSalas/<str:pk>/', editarSalas_View, name='editarsalas'),
    path('deletarSalas/<str:pk>/', deletarSalas_View, name='deletarsalas'),
    path('editarHorarios/<str:pk>/', editarHorarios_View, name='editarhorarios'),
    path('deletarHorarios/<str:pk>/', deletarHorarios_View, name='deletarhorarios'),
    path('deletarPavilhoes/<str:pk>/', deletarPavilhoes_View, name='deletarpavilhoes'),
    path('editarPavilhoes/<str:pk>/', editarPavilhoes_View, name='editarpavilhoes'),
]