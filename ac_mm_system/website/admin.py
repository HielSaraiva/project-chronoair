from django.contrib import admin

from .models import Pavilhao, Horario, Sala

@admin.register(Pavilhao)
class PavilhaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'numero_salas')

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('pavilhao','dias_da_semana','horario_inicio','horario_fim')

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pavilhao', 'horario')