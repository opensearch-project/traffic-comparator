# syntax=docker/dockerfile:1
FROM python:3.10.10

RUN apt-get update && apt-get install -y netcat

WORKDIR /traffic_comparator

# Copying the local necessary files for the comparator to run is only temporary, until the comparator repo is public.
# Then the steps here would be to clone the repo.
VOLUME /traffic_comparator

CMD docker/run_app.sh

