import datetime
import sys
from django.contrib import messages
from django.contrib.messages import get_messages

def management_handling():
    """
    This is a hacky attempt to stop loading the full app during
    commands like migrate and so on
    """
    # add more as they get discovered
    managers = {
        "migrate",
        "makemigrations",
        "do_ocr",
        "parse_latest_ocr",
        "createsuperuser",
        "reload",
        "load_languages",
        "load_corpora"
    }
    return any(i in managers for i in sys.argv)


def _make_message(request, level, msg, safe=True):
    """
    Just add the message once
    """
    safe = dict(extra_tags='safe') if safe else {}
    safe = {}
    if msg not in [m.message for m in get_messages(request)]:
        messages.add_message(request, level, msg, **safe)


def delete_old_tables():
    return
    print("LOOKING FOR OLD TABLES TO DELETE")
    from start.apps import user_tables
    from django.conf import settings
    max_hours = settings.USER_TABLES_MAX_AGE_HOURS
    to_remove = []
    for k, v in user_tables.items():
        timestamp = k[-1]
        delta = datetime.datetime.now() - datetime.timedelta(hours=max_hours)
        if timestamp < delta:
            to_remove.append(k)
    for too_old in to_remove:
        print("DELETING TABLE", too_old)
        user_tables.pop(too_old)
