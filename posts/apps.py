import os
from django.apps import AppConfig
from ultralytics import YOLO

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
    verbose_name = 'Посты'


    model = None

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE'):
            PostsConfig.model = YOLO("yolov8m.pt")


