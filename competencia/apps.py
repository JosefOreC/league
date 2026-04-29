from django.apps import AppConfig


class CompetenciaConfig(AppConfig):
    name = 'competencia'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import competencia.infrastructure.adapters.output.models 
