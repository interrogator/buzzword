FROM python:3.7-slim-buster

RUN apt-get update && \
    apt-get install -y git build-essential nginx tesseract-ocr libtesseract-dev

WORKDIR /

RUN \
    git clone https://github.com/interrogator/buzz.git buzz && \
    cd buzz && \
    pip install -r requirements.txt && \
    python setup.py install

RUN \
    git clone https://github.com/interrogator/buzzword.git && \
    cd buzzword && \
    git pull --all && \
    git checkout swisslaw && \
    pip install -r requirements.txt

WORKDIR /buzzword

RUN \
    cp configs/swiss-law.json corpora.json && \
    echo "BUZZWORD_SPECIFIC_CORPUS = 'swiss-law'" >> buzzword/settings.py && \
    echo "DEBUG = False" >> buzzword/settings.py

# COPY buzzword/swiss-law/swiss-law-parsed /buzzword/swiss-law/swiss-law-parsed

# RUN python manage.py migrate

RUN chown www-data:www-data . && \
    chmod 777 . && \
    touch db.sqlite3 && \
    chown www-data:www-data db.sqlite3 && \
    chmod 777 db.sqlite3

RUN \
    pip install uwsgi && \
    ln -s /buzzword/buzzword_nginx.conf /etc/nginx/sites-enabled/

#CMD python manage.py runserver 0.0.0.0:8000
CMD service nginx start && uwsgi --ini /buzzword/uwsgi-docker.ini
