#!/usr/bin/env bash

# deployment script to run on server for buzzword swisslaw

# Run it like this. Container name will be buzzword_[BRANCH_NAME]
# ./deploy.sh [DJANGO PASSWORD] [BRANCH_NAME]

# Parse command-line options

# Option strings
SHORT=b:d:c:
LONG=branch:,django-password:,corpus:,corpus-file:,no-cache,cwdmount,port:

# read the options
OPTS=$(getopt --options $SHORT --long $LONG --name "$0" -- "$@")

if [ $? != 0 ] ; then echo "Failed to parse options...exiting." >&2 ; exit 1 ; fi

eval set -- "$OPTS"

# set initial values
BRANCH="master"
DJANGO_SUPERUSER_PASSWORD=""
CORPUS=""
CORPUS_FILE=""
NOCACHE=""
CWDMOUNT=false
PORT=80

while true ; do
  case "$1" in
    -b | --branch )
      BRANCH="$2"
      shift 2
      ;;
    -d | --django-password )
      DJANGO_SUPERUSER_PASSWORD="$2"
      shift 2
      ;;
    -c | --corpus )
      CORPUS="--build-arg CORPUS=$2"
      shift 2
      ;;
    --corpus-file )
      CORPUS_FILE="--build-arg CORPUS_FILE=$2"
      shift 2
      ;;
    --port )
      PORT=$2
      shift 2
      ;;
    --no-cache )
      NOCACHE="--no-cache"
      shift
      ;;
    --cwdmount )
      CWDMOUNT=true
      shift
      ;;
    -- )
      shift
      break
      ;;
  esac
done

NAME="buzzword_$BRANCH"
TAG="buzzword:$BRANCH"

if [ -z "$(git show-ref refs/heads/$BRANCH)" ]; then
    echo "Branch $BRANCH does not exist."
    exit 1
fi

# get latest repo
#git checkout $BRANCH
git pull

# build the image (note, data is still missing)
BUILD_BRANCH="--build-arg BRANCH=$BRANCH"
sudo docker build - < Dockerfile $CORPUS $CORPUS_FILE $BUILD_BRANCH $NOCACHE -t $TAG

# now kill and delete the old container if running
sudo docker stop $NAME
sudo docker container rm $NAME

touch db.sqlite3

if $CWDMOUNT ; then
    MOUNT="
        --mount type=bind,source="$(pwd)",target=/buzzword
    "
else
    # add settings, db and data in as volume
    MOUNT="
        --mount type=bind,source="$(pwd)"/buzzword/settings.py,target=/buzzword/buzzword/settings.py
        --mount type=bind,source="$(pwd)"/db.sqlite3,target=/buzzword/db.sqlite3
        --mount type=bind,source="$(pwd)"/static/corpora,target=/buzzword/static/corpora
    "
fi

sudo docker run -itd -p $PORT:8000 $MOUNT -e "DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD" --name $NAME $TAG

# all the commands we need to do to get configured
sudo docker exec -it $NAME python manage.py migrate
sudo docker exec -it $NAME python manage.py load_languages
sudo docker exec -it $NAME python manage.py load_corpora
sudo docker exec -it $NAME python manage.py do_ocr
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superusers with password: $DJANGO_SUPERUSER_PASSWORD"
    sudo docker exec -it $NAME python manage.py createsuperuser --noinput --username danny --email danny@testing.com
    sudo docker exec -it $NAME python manage.py createsuperuser --noinput --username martin.kurz --email martin@testing.com
fi

echo "Container name: $NAME"


