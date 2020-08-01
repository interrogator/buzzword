import os
from importlib import import_module

from explorer.main import load_explorer_app
from explore.models import Corpus
from compare.load import load_tif_pdf_plaintext
from django.apps import apps
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)
from django.core.management.color import no_style
from django.core.management.sql import emit_post_migrate_signal, sql_flush
from django.db import DEFAULT_DB_ALIAS, connections
from django.conf import settings

class Command(RunServerCommand):

    # def __init__(self, *args, **kwargs):
    #   super().__init__(self, *args, **kwargs)

    def run(self, **options):

        database = options.get("database", DEFAULT_DB_ALIAS)
        connection = connections[database]
        verbosity = options["verbosity"]
        interactive = False
        # The following are stealth options used by Django's internals.
        reset_sequences = options.get("reset_sequences", True)
        allow_cascade = options.get("allow_cascade", False)
        inhibit_post_migrate = options.get("inhibit_post_migrate", False)

        self.style = no_style()

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            try:
                import_module(".management", app_config.name)
            except ImportError:
                pass

        sql_list = sql_flush(
            self.style,
            connection,
            only_django=True,
            reset_sequences=reset_sequences,
            allow_cascade=allow_cascade,
        )

        print("Flushing database!")
        connection.ops.execute_sql_flush(database, sql_list)
        if sql_list and not inhibit_post_migrate:
            # Emit the post migrate signal. This allows individual applications to
            # respond as if the database had been migrated from scratch.
            emit_post_migrate_signal(verbosity, interactive, database)

        corpora_file = os.path.abspath(settings.CORPORA_FILE)

        print(f"Done. Loading from {corpora_file}")

        # see https://code.djangoproject.com/ticket/8085
        if os.environ.get("RUN_MAIN", False):
            load_explorer_app()
            for corpus in Corpus.objects.all():
                if corpus.pdfs and not corpus.disabled:
                    os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX
                    load_tif_pdf_plaintext(corpus)
