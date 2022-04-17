#!/bin/sh

if [ "$DATABASE" = "movies_database" ]
then
    echo "Postgres еще не запущен..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "Postgres запущен"
fi

python manage.py collectstatic --no-input --clear
python manage.py migrate
python manage.py loaddata data.json

exec "$@"
