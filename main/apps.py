from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
    def ready(self):
        from .scheduler import start_scheduler
        from .ml.predictor import load_model
        start_scheduler()
        load_model()