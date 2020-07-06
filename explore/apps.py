from django.apps import AppConfig

# note about why the ready() code is a bad idea:
# docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready
# Although you can access model classes as described above, avoid interacting 
# with the database in your ready() implementation. This includes model methods
# that execute queries (save(), delete(), manager methods etc.), and also raw
# SQL queries via django.db.connection. Your ready() method will run during
# startup of every management command. For example, even though the test
# database configuration is separate from the production settings, 
# manage.py test would still execute some queries against your prod database!

class ExploreConfig(AppConfig):
    name = "explore"
    def ready(self):
    	try:
            print("Loading corpora from apps.py!")
            import explorer.parts.main
            explorer.parts.main.load_corpora()
        except:
        	print("Load corpora from apps.py failed (OK during migrate etc)")
        super().ready()
