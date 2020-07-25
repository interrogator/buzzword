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
        "reload"
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
