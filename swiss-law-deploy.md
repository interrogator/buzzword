# Deployment instructions for *swiss-law* app

* master branch is the full app, designed for multiple corpora
* swisslaw branch is the most up-to-date, used for the swiss-law project in a single corpus view.

On server:

```bash
git checkout swisslaw
git pull
# build the image (note, data is still missing)
sudo docker build - < Dockerfile --no-cache -t buzzword:swisslaw
```

Dockerfile should have done the configuration for swiss-law:

* Use `configs/swiss-law.json` as `corpora.json`
* Set `settings.BUZZWORD_SPECIFIC_CORPUS = "swiss-law"`

Run container, mounting the corpora directory and DB, and save the container ID as a variable:

```bash
ID=$(sudo docker run -itd -p 80:8000 \
    --mount type=bind,source="$(pwd)"/static/corpora,target=/buzzword/static/corpora \
    --mount type=bind,source="$(pwd)"/db.sqlite3,target=/buzzword/db.sqlite3 \
    buzzword:swisslaw 2>&1)
```

Now management commands can be used to do OCR and parse the results.


```bash
# must do this one first
sudo docker exec -it $ID python manage.py migrate && \
    # load language model info
    sudo docker exec -it $ID python manage.py load_languages && \
    # loads contents of corpora.json into models
    sudo docker exec -it $ID python manage.py load_corpora && \
    # do ocr for corpora with pdfs=True (accepts slug as arg)
    # for this there should be data in static/corpora/swiss-law/tiff
    sudo docker exec -it $ID python manage.py do_ocr && \
    # create our superusers, who can access admin/login
    sudo docker exec -it $ID python manage.py createsuperuser
# dump latest OCR edits to static/corpora/swiss-law/txt and parse it
sudo docker exec -it $ID python manage.py parse_latest_ocr
# flush ALL db data and load corpora in (conllu needs to have data)
# docker exec -it $ID python manage.py reload
```

Admin site is at: `https://<server>:8000/admin/login`

Finally, go to the site and explore the corpus, to make sure it is correctly loaded...
