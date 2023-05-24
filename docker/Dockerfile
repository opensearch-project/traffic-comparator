# syntax=docker/dockerfile:1
FROM python:3.10.10

RUN apt-get update && apt-get install -y netcat

WORKDIR /traffic_comparator
RUN mkdir /traffic_comparator/traffic_comparator
COPY traffic_comparator /traffic_comparator/traffic_comparator/
COPY setup.py /traffic_comparator/
COPY cli.py /traffic_comparator/

COPY docker/run_app.sh ./run_app.sh

RUN pip3 install --editable .

CMD ./run_app.sh

