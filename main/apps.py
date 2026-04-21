from django.apps import AppConfig
import os

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            from .scheduler import start_scheduler
            start_scheduler()