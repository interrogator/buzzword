#!/usr/bin/env bash

# deployment script to run on server for buzzword swisslaw

# Run it like this to get the container ID:

#     ID=$(./configs/swiss-law-deploy.sh)

echo "MAKE SURE YOU SET PASSWORD ENVIRONMENT VARIABLE: $PASSWORD"

git checkout swisslaw
git pull

# build the image (note, data is still missing)
sudo docker build - < Dockerfile --build-arg DJANGO_SUPERUSER_PASSWORD=$PASSWORD --no-cache -t buzzword:swisslaw

# add settings and data in as volume
ID=$(sudo docker run -itd -p 80:8000 \
    --mount type=bind,source="$(pwd)"/buzzword/settings.py,target=/buzzword/buzzword/settings.py \
    --mount type=bind,source="$(pwd)"/static/corpora,target=/buzzword/static/corpora \
    buzzword:swisslaw 2>&1)

sudo docker exec -it $ID python manage.py migrate
sudo docker exec -it $ID python manage.py load_languages
sudo docker exec -it $ID python manage.py load_corpora
sudo docker exec -it $ID python manage.py do_ocr
echo "Creating superusers with password: $PASSWORD"
sudo docker exec -it $ID python manage.py createsuperuser --noinput --username danny --email danny@swisslaw.com
sudo docker exec -it $ID python manage.py createsuperuser --noinput --username martin.kurz --email martin@swisslaw.com

echo "$ID"
