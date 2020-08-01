from django.apps import AppConfig
from explorer.main import _get_or_load_corpora
from buzzword.utils import management_handling

class StartConfig(AppConfig):
    name = "start"

    def ready(self):
        # Singleton utility
        # We load them here to avoid multiple instantiation across other
        # modules, that would take too much time.
        if not management_handling():
            global corpora, initial_tables, initial_concs
            print("Loading corpora in AppConfig")
            corpora, initial_tables, initial_concs = _get_or_load_corpora(force=False)
            print("AppConfig loaded")
        else:
            print("Not loading data because this is a management command.")
