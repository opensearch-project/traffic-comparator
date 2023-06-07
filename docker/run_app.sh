#!/bin/bash

while true
do
  nc -v -l -p 9220 | tee /dev/stderr | trafficcomparator -vv stream | trafficcomparator dump-to-sqlite --db $1
  >&2 echo "Command has encountered error. Restarting now ..."
  sleep 1
done
