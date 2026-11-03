from django.apps import AppConfig


class AssessmentsConfig(AppConfig):
    name = 'assessments'

    def ready(self):
        from . import branch_sync
        from . import marketing_sync
