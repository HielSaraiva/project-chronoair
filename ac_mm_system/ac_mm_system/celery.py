import os
from celery import Celery
from website.tasks_mqtt import *  # Importa todas as tasks do módulo tasks_mqtt


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ac_mm_system.settings')

app = Celery('ac_mm_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
