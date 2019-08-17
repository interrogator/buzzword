"""
Make a workspace for buzzword in the current directory
"""

import os
import sys

from buzz.corpus import Corpus

NAME = sys.argv[-1]

FULLNAME = os.path.abspath(NAME)
CORPUS_PATH = os.path.join(NAME, "example")

print("Making a new workspace at {}".format(FULLNAME))

ENV = """
# .env example for deploying buzzword
# comment out keys you are not using
BUZZWORD_CORPORA_FILE=corpora.json
BUZZWORD_ROOT={}
BUZZWORD_LOAD=true
BUZZWORD_TITLE=buzzword
BUZZWORD_DEBUG=false
# BUZZWORD_MAX_DATASET_ROWS=999999
BUZZWORD_DROP_COLUMNS=parse,text
BUZZWORD_PAGE_SIZE=25
BUZZWORD_TABLE_SIZE=2000,200
BUZZWORD_ADD_GOVERNOR=false
""".format(FULLNAME)

CORPORA = """
{{
  "Example corpus: joke": {{
    "slug": "jokes",
    "path": "{}",
    "desc": "Sample corpus with speaker names and metadata",
    "len": 29,
    "drop_columns": ["text"],
    "disable": false,
    "date": "2019",
    "url": "https://en.wikipedia.org/wiki/Joke"
    }}
}}
""".format(
    os.path.abspath(CORPUS_PATH + "-parsed")
)

CORPUS = """
<meta doc-type="joke" rating=6.50 speaker="NARRATOR"/>
<meta being="animal">A lion</meta> and <meta being="animal">a cheetah</meta> decide to race. 
<meta move="setup" dialog=false punchline=false some-schema=9 />
The cheetah crosses the finish line first. <meta move="setup" dialog=false punchline=false />
CHEETAH: I win! <meta move="middle" dialog=true some-schema=2 />
LION: You're a <meta play-on="cheater">cheetah</meta>! <meta move="punchline" funny=true dialog=true some-schema=3 />
CHEETAH: You're <meta play-on="lying">lion</meta>! <meta move="punchline" funny=true dialog=true some-schema=4 rating=7.8 />
"""

os.makedirs(NAME)

for folder in ["csv", "uploads", "example"]:
    os.makedirs(os.path.join(NAME, folder))
with open(os.path.join(NAME, ".env"), "w") as fo:
    fo.write(ENV)
with open(os.path.join(NAME, "corpora.json"), "w") as fo:
    fo.write(CORPORA)
with open(os.path.join(CORPUS_PATH, "001-joke-lion-pun.txt"), "w") as fo:
    fo.write(CORPUS)
print("Testing parser: {}->{}-parsed ...".format(CORPUS_PATH, CORPUS_PATH))
parsed = Corpus(CORPUS_PATH).parse(cons_parser=None)

print("Workspace made in {}".format(FULLNAME))
print("Run 'cd {} && python -m buzzword' to start.".format(NAME))
