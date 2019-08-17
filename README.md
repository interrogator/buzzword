# buzzword

> Version 1.1.1

[![Build Status](https://travis-ci.org/interrogator/buzzword.svg?branch=master)](https://travis-ci.org/interrogator/buzzword)
[![readthedocs](https://readthedocs.org/projects/buzzword/badge/?version=latest)](https://buzzword.readthedocs.io/en/latest/)
[![codecov.io](https://codecov.io/gh/interrogator/buzzword/branch/master/graph/badge.svg)](https://codecov.io/gh/interrogator/buzzword)
[![PyPI version](https://badge.fury.io/py/buzzword.svg)](https://badge.fury.io/py/buzzword)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

> Web-app for corpus linguistics; documentation available [via ReadTheDocs](https://buzzword.readthedocs.io/en/latest/)

## Install buzzword

```bash
pip install buzzword
```

## Quickstart

```bash
python -m buzzword.create workspace
cd workspace
python -m buzzword
```

## Setup

0. [Create and parse corpus](https://buzzword.readthedocs.io/en/latest/building/)
1. [Configure a `.env` file](https://buzzword.readthedocs.io/en/latest/run/) from `.env.example`
2. [Configure a `corpora.json`](https://buzzword.readthedocs.io/en/latest/run/) file from `corpora.json.example`
3. Run the tool with or without command line arguments:

```bash
buzzword --debug
# or
python -m buzzword --debug
```
