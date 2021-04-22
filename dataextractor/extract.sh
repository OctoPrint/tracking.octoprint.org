#!/bin/sh

URL=$1
EXPORT=$2

# instance stats
./venv/bin/python extract_instance_stats.py "$URL" 7 "$EXPORT/instance_stats_7d.json"
./venv/bin/python extract_instance_stats.py "$URL" 30 "$EXPORT/instance_stats_30d.json"

# plugin stats
./venv/bin/python extract_plugin_stats.py "$URL" 7 "$EXPORT/plugin_stats_7d.json"
./venv/bin/python extract_plugin_stats.py "$URL" 30 "$EXPORT/plugin_stats_30d.json"

# python stats
./venv/bin/python extract_python_stats.py "$URL" 7 "$EXPORT/python_stats_7d.json"
./venv/bin/python extract_python_stats.py "$URL" 30 "$EXPORT/python_stats_30d.json"

# printing stats
./venv/bin/python extract_printing_stats.py "$URL" 7 "$EXPORT/printing_stats_7d.json"
./venv/bin/python extract_printing_stats.py "$URL" 30 "$EXPORT/printing_stats_30d.json"
