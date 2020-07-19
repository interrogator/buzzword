import sys


def management_handling():
    """
    This is a hacky attempt to stop loading the full app during
    commands like migrate and so on
    """
    managers = {"migrate", "makemigrations", "do_ocr", "parse_latest_ocr"}
    return any(i in managers for i in sys.argv)
