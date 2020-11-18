FROM python:3.7-slim-buster

RUN apt-get update && \
    apt-get install -y git build-essential nginx tesseract-ocr libtesseract-dev

RUN pip install --upgrade pip

WORKDIR /

RUN \
    git clone https://github.com/interrogator/buzz.git buzz && \
    cd buzz && \
    pip install -r requirements.txt && \
    python setup.py install

ARG BRANCH=master

RUN \
    git clone https://github.com/interrogator/buzzword.git && \
    cd buzzword && \
    git pull --all && \
    git checkout $BRANCH && \
    pip install -r requirements.txt

WORKDIR /buzzword

ARG CORPUS
ARG CORPUS_FILE

RUN if [ -n "$CORPUS" ] ; then echo "BUZZWORD_SPECIFIC_CORPUS = '$CORPUS'" >> buzzword/settings.py ; fi
RUN if [ -n "$CORPUS_FILE" ] ; then cp $CORPUS_FILE corpora.json ; else cp corpora.json.example corpora.json ; fi

RUN chown www-data:www-data . && \
    chmod 777 . && \
    touch db.sqlite3 && \
    chown www-data:www-data db.sqlite3 && \
    chmod 777 db.sqlite3

RUN \
    pip install uwsgi && \
    ln -s /buzzword/buzzword_nginx.conf /etc/nginx/sites-enabled/

CMD service nginx start && uwsgi --ini /buzzword/uwsgi-docker.ini
