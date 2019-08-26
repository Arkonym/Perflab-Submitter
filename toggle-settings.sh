#! /bin/bash

if [ -f ./prod-docker-compose.yml ]; then
  echo "prod compose exists"
  mv ./docker-compose.yml ./local-docker-compose.yml
  echo "renamed local"
  mv ./prod-docker-compose.yml ./docker-compose.yml
  echo "renamed prod"
  if [ -f ./web/perfproject/prod-settings.py ]; then
    echo "prod settings exists"
    mv ./web/perfproject/settings.py ./web/perfproject/local-settings.py
    echo "renamed local"
    mv ./web/perfproject/prod-settings.py ./web/perfproject/settings.py
    echo "renamed prod"
  fi
elif [ -f ./local-docker-compose.yml ]; then
  echo "local compose exists"
  mv ./docker-compose.yml ./prod-docker-compose.yml
  echo "renamed prod"
  mv ./local-docker-compose.yml ./docker-compose.yml
  echo "renamed local"
  if [ -f ./web/perfproject/local-settings.py ]; then
    echo "local settings exists"
    mv ./web/perfproject/settings.py ./web/perfproject/prod-settings.py
    echo "renamed prod"
    mv ./web/perfproject/local-settings.py ./web/perfproject/settings.py
    echo "renamed local"
  fi
fi
