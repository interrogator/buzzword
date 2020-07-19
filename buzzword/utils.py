import sys
from django.contrib import messages
from django.contrib.messages import get_messages

def management_handling():
    """
    This is a hacky attempt to stop loading the full app during
    commands like migrate and so on
    """
    managers = {"migrate", "makemigrations", "do_ocr", "parse_latest_ocr"}
    return any(i in managers for i in sys.argv)


def _make_message(request, level, msg):
    """
    Just add the message once
    """
    if msg not in [m.message for m in get_messages(request)]:
        messages.add_message(request, level, msg)
