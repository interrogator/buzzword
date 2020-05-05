#!/usr/bin/env python

"""
python -m buzzword
python -m buzzword runserver
python -m buzzword reload
etc
"""
import os
import sys

import pathlib

from django.core.management import execute_from_command_line

CWD = os.getcwd()

manage_dir = pathlib.Path(__file__).parent.parent.absolute()
os.chdir(manage_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buzzword.settings")
os.environ.setdefault("BUZZWORD_CORPORA_FILE", os.path.join(CWD, "corpora.json"))
os.environ.setdefault("BUZZWORD_ROOT", CWD)

if len(sys.argv) == 1 and "__main__.py" in sys.argv[0]:
    argv = ["manage.py", "runserver"]
elif len(sys.argv) > 1:
    argv = ["manage.py", *sys.argv[1:]]
else:
    argv = sys.argv

execute_from_command_line(argv)
