from django.apps import AppConfig


class ExploreConfig(AppConfig):
    name = "explore"
    def ready(self):
        print("Loading corpora from urls.py!")
        import explorer.parts.main
        explorer.parts.main.load_corpora()
