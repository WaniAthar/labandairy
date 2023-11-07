from django.apps import AppConfig


class LabanmanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'labanmanagement'
    def ready(self) -> None:
        import labanmanagement.signals
        return super().ready()
