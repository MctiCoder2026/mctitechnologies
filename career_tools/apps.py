from django.apps import AppConfig


class CareerToolsConfig(AppConfig):
    name = 'career_tools'

    def ready(self):
        from assessments import marketing_sync
