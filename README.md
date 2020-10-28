# buzzword

> Version 1.4.0

[![Build Status](https://travis-ci.org/interrogator/buzzword.svg?branch=master)](https://travis-ci.org/interrogator/buzzword)
[![readthedocs](https://readthedocs.org/projects/buzzword/badge/?version=latest)](https://buzzword.readthedocs.io/en/latest/)
[![codecov.io](https://codecov.io/gh/interrogator/buzzword/branch/master/graph/badge.svg)](https://codecov.io/gh/interrogator/buzzword)
[![PyPI version](https://badge.fury.io/py/buzzword.svg)](https://badge.fury.io/py/buzzword)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

> Web-app for corpus linguistics; documentation available [via ReadTheDocs](https://buzzword.readthedocs.io/en/latest/)

> Note, this app is currently being overhauled and turned into a Django project. The last stable (Dash) app was version `1.2.5`. Versions after this will be in Django, and for now, a bit unstable, as features like user management are added in. Documentation for now targets 1.2.5, not the new Django app.

## Setup

1. Clone this repo
2. Create some data
3. Configure settings.py
4. Configure corpora.json
5. Start the server:

```bash
python manage.py runserver
```

## Reloading corpora.json

If you modify `corpora.json`, you can reload things with the custom command:

```bash
python manage.py reload
```

## Run from Dockerfile

```bash
docker build . -t name/tag
docker run -it -p 8001:8000 name/tag
```

*buzzword* is now available at http://localhost:8001


## Run with deploy script

```bash
./deploy.sh
```
The deploy script supports a number of parameters:
- `--port=xx` to set which port (of the docker host) the app should run on 
- `--branch=name` or `-b=name` pick any branch that exists in git
- `--no-cache` when this option is present docker build will run without cache (recommended for production)
- `--corpus=name` or `-c=name` configure app to be in single-corpus mode
- `--corpuse-file=path` copy a custom corpora.json into the container
- `--cwdmount` mount the current working directory as `/buzzword` (recommended for dev)
- `--django-password=pw` or `-d=pw` create super user account with the given password

