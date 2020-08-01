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

RUN \
    git clone https://github.com/interrogator/buzzword.git && \
    cd buzzword && \
    pip install -r requirements.txt

WORKDIR /buzzword


RUN chown www-data:www-data . && \
    chmod 777 . && \
    touch db.sqlite3 && \
    chown www-data:www-data db.sqlite3 && \
    chmod 777 db.sqlite3

RUN chown www-data:www-data . && \
    chmod 777 . && \
    chown www-data:www-data db.sqlite3 && \
    chmod 777 db.sqlite3

RUN \
    pip install uwsgi && \
    ln -s /buzzword/buzzword_nginx.conf /etc/nginx/sites-enabled/

CMD service nginx start && uwsgi --ini /buzzword/uwsgi-docker.ini
