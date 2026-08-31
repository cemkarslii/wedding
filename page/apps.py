from django.apps import AppConfig


class PageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "page"
    verbose_name = "Düğün İçerikleri"

    def ready(self):
        from page import signals  # noqa: F401
