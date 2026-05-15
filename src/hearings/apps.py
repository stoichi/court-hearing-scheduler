from django.apps import AppConfig


class HearingsConfig(AppConfig):
    name = 'hearings'

    def ready(self) -> None:
        # Import signals to register it and enable it
        import hearings.signals  # noqa: F401
