#!/bin/bash

URL=$1
EXPORT=$2
PYTHON=./venv/bin/python

STATS=("instance" "plugin" "python" "printing" "server_environment" "client_environment" "firmware" "rpi")
DAYS=(7 30)
for stat in "${STATS[@]}"; do
  for days in "${DAYS[@]}"; do
    $PYTHON "extract_${stat}_stats.py" "$URL" $days "$EXPORT/${stat}_stats_${days}d.json"
  done
done