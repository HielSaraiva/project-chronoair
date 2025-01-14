from django.urls import path

from . import views

app_name = "website_test"
urlpatterns = [
    # Página inicial
    path("", views.index, name="index"),
]