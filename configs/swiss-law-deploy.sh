#!/usr/bin/env bash

# deployment script to run on server for buzzword swisslaw

# Run it like this. Container name will be buzzword_[BRANCH_NAME]
# ./configs/swiss-law-deploy.sh [DJANGO PASSWORD] [BRANCH_NAME]

if [ "$#" -ne 2 ]; then
    echo "exactly 2 params needed: deploy.sh [DJANGO_PASSWORD] [BRANCH_NAME]"
    exit 1
fi

DJANGO_SUPERUSER_PASSWORD="$1"
BRANCH="$2"
NAME="buzzword_$BRANCH"
TAG="buzzword:$BRANCH"


if [ -z "$(git show-ref refs/heads/$BRANCH)" ]; then
    echo "Branch $BRANCH does not exist."
    exit 1
fi

# ensure db file is there (not required to this here since db is inside container)
# touch db.sqlite3
# sudo chown www-data:www-data db.sqlite3
# sudo chmod 777 db.sqlite3

# get latest repo
git checkout $BRANCH
git pull

# build the image (note, data is still missing)
#sudo docker build - < Dockerfile --build-arg DJANGO_SUPERUSER_PASSWORD=$PASSWORD --no-cache -t buzzword:swisslaw
sudo docker build - < Dockerfile --no-cache -t $TAG

# now kill and delete the old container if running
sudo docker stop $NAME
sudo docker container rm $NAME
# sudo docker container kill $(docker ps -q)

# add settings, db and data in as volume
ID=$(sudo docker run -itd -p 8080:8000 \
    --mount type=bind,source="$(pwd)"/buzzword/settings.py,target=/buzzword/buzzword/settings.py \
    --mount type=bind,source="$(pwd)"/static/corpora,target=/buzzword/static/corpora \
    -e "DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD" \
    --name $NAME \
    $TAG 2>&1)

# all the commands we need to do to get configured
sudo docker exec -it $ID python manage.py migrate
sudo docker exec -it $ID python manage.py load_languages
sudo docker exec -it $ID python manage.py load_corpora
sudo docker exec -it $ID python manage.py do_ocr
echo "Creating superusers with password: $DJANGO_SUPERUSER_PASSWORD"
sudo docker exec -it $ID python manage.py createsuperuser --noinput --username danny --email danny@testing.com
sudo docker exec -it $ID python manage.py createsuperuser --noinput --username martin.kurz --email martin@testing.com

echo "$NAME"


