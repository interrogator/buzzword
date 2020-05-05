#!/usr/bin/env python3

"""
buzzword: make a workspace for buzzword in the current directory

Usage: python -m buzzword.create <name>

Once a workspace is defined, you can cd in there and run buzzword.

You can modify the various config and data files as you see fit.
"""

import os
import sys

from buzz import Corpus

NAME = sys.argv[-1]

FULLNAME = os.path.abspath(NAME)

if "create.py" in FULLNAME:
    raise ValueError("Please specify a name for your project.")

if os.path.exists(FULLNAME):
    raise OSError(f"Path exists: {FULLNAME}")

CORPUS_PATH = os.path.join(NAME, "example")

print("Making a new workspace at {}".format(FULLNAME))

ENV = f"""
# .env example for deploying buzzword
# comment out keys you are not using
BUZZWORD_CORPORA_FILE=corpora.json
BUZZWORD_ROOT={FULLNAME}
BUZZWORD_LOAD=true
BUZZWORD_DEBUG=false
BUZZWORD_MAX_DATASET_ROWS=999999
BUZZWORD_DROP_COLUMNS=parse,text
BUZZWORD_PAGE_SIZE=25
BUZZWORD_TABLE_SIZE=2000,200
BUZZWORD_ADD_GOVERNOR=false
"""

CORPORA = f"""
{{
  "Example corpus: joke": {{
    "slug": "jokes",
    "path": "{os.path.abspath(CORPUS_PATH + "-parsed")}",
    "desc": "Sample corpus with speaker names and metadata",
    "len": 29,
    "drop_columns": ["text"],
    "disable": false,
    "date": "2019",
    "url": "https://en.wikipedia.org/wiki/Joke"
    }}
}}
"""

CORPUS = """
<meta doc-type="joke" rating=6.50 speaker="NARRATOR"/>
<meta being="animal">A lion</meta> and <meta being="animal">a cheetah</meta> decide to race. <meta move="setup" dialog=false punchline=false some-schema=9 />
The cheetah crosses the finish line first. <meta move="setup" dialog=false punchline=false />
CHEETAH: I win! <meta move="middle" dialog=true some-schema=2 />
LION: You're a <meta play-on="cheater">cheetah</meta>! <meta move="punchline" funny=true dialog=true some-schema=3 />
CHEETAH: You're <meta play-on="lying">lion</meta>! <meta move="punchline" funny=true dialog=true some-schema=4 rating=7.8 />
"""

os.makedirs(FULLNAME)

for folder in ["csv", "uploads", "example"]:
    os.makedirs(os.path.join(FULLNAME, folder))
with open(os.path.join(FULLNAME, ".env"), "w") as fo:
    fo.write(ENV.strip() + "\n")
with open(os.path.join(FULLNAME, "corpora.json"), "w") as fo:
    fo.write(CORPORA.strip() + "\n")
with open(os.path.join(CORPUS_PATH, "001-joke-lion-pun.txt"), "w") as fo:
    fo.write(CORPUS.strip() + "\n")
print(f"Testing parser: {CORPUS_PATH}->{CORPUS_PATH}-parsed ...")

parsed = Corpus(CORPUS_PATH).parse(constituencies=False)

print(f"Workspace made in {FULLNAME}")
print(f"Run 'cd {NAME} && python -m buzzword' to start.")
