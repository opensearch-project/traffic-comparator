#!/bin/bash

while true
do
  nc -v -l -p 9220 | tee /dev/stderr | trafficcomparator -vv stream | trafficcomparator stream-report
  >&2 echo "Command has encountered error. Restarting now ..."
  sleep 1
done

