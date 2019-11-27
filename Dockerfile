FROM python:3.7-buster

WORKDIR /

RUN \
    git clone https://github.com/interrogator/buzz.git buzz && \
    cd buzz && \
    pip install -r requirements.txt

RUN \
    git clone https://github.com/l0rb/buzzword.git buzzword && \
    cd buzzword && \
    pip install -r requirements.txt

RUN pip install dash_bootstrap_components

WORKDIR /buzzword
RUN \
    cp .env.example .env && \
    cp corpora.json.example corpora.json && \
    sed -i 's!dtrt/do-the-right-thing-parsed!/buzz/dtrt/do-the-right-thing-parsed!' corpora.json && \
    sed -i '0,/disabled/! s/"disabled": false/"disabled": true/' corpora.json

RUN python manage.py migrate

CMD python manage.py runserver 0.0.0.0:8000
