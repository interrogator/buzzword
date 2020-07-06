"""
WSGI config for buzzword project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import django
django.setup()
from django.conf import settings
settings.configure()

import explorer.parts.main

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buzzword.settings")

explorer.parts.main.load_corpora()
application = get_wsgi_application()
