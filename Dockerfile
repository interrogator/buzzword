FROM python:3.7-slim-buster

RUN apt-get update && \
    apt-get install -y git build-essential nginx tesseract-ocr libtesseract-dev

WORKDIR /

RUN \
    git clone https://github.com/interrogator/buzz.git buzz && \
    cd buzz && \
    pip install -r requirements.txt

RUN \
    git clone https://github.com/l0rb/buzzword.git buzzword && \
    cd buzzword && \
    pip install -r requirements.txt

WORKDIR /buzzword

RUN \
    cp .env.example .env && \
    cp corpora.json.example corpora.json && \
    sed -i 's!dtrt/do-the-right-thing-parsed!/buzz/dtrt/do-the-right-thing-parsed!' corpora.json

RUN python manage.py migrate

RUN \
    pip install uwsgi && \
    ln -s /buzzword/buzzword_nginx.conf /etc/nginx/sites-enabled/

#CMD python manage.py runserver 0.0.0.0:8000
CMD service nginx start && uwsgi --ini /buzzword/uwsgi-docker.ini
