import datetime
import io
import json
import sys
import time

import requests

URL = sys.argv[1]
DAYS = int(sys.argv[2])
OUTPUT = sys.argv[3]

NOW = time.time()
CUTOFF = int((NOW - DAYS * 24 * 60 * 60) * 1000)
CUTOFF_HISTOGRAM = int(
    datetime.datetime.fromtimestamp(NOW - DAYS * 24 * 60 * 60)
    .replace(minute=0, second=0, microsecond=0)
    .timestamp()
    * 1000
)

QUERY_PYTHON_VERSION = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.python.keyword",
                "order": {"1": "desc"},
                "size": 1000,
                "min_doc_count": 1,
            },
            "aggs": {"1": {"cardinality": {"field": "uuid.keyword"}}},
        }
    },
    "size": 0,
    "query": {
        "bool": {
            "must": [{"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}}]
        }
    },
}

QUERY_PYTHON2_HISTOGRAM = {
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                {
                    "range": {
                        "@timestamp": {"gte": CUTOFF_HISTOGRAM, "format": "epoch_millis"}
                    }
                },
                {
                    "query_string": {
                        "analyze_wildcard": True,
                        "query": "payload.python:2.*",
                    }
                },
            ]
        }
    },
    "aggs": {
        "1": {
            "date_histogram": {
                "interval": "1d",
                "field": "@timestamp",
                "min_doc_count": 0,
                "format": "epoch_millis",
            },
            "aggs": {"2": {"cardinality": {"field": "uuid.keyword"}}},
        }
    },
}

QUERY_PYTHON3_HISTOGRAM = {
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                {
                    "range": {
                        "@timestamp": {"gte": CUTOFF_HISTOGRAM, "format": "epoch_millis"}
                    }
                },
                {
                    "query_string": {
                        "analyze_wildcard": True,
                        "query": "payload.python:3.*",
                    }
                },
            ]
        }
    },
    "aggs": {
        "1": {
            "date_histogram": {
                "interval": "1d",
                "field": "@timestamp",
                "min_doc_count": 0,
                "format": "epoch_millis",
            },
            "aggs": {"2": {"cardinality": {"field": "uuid.keyword"}}},
        }
    },
}

_since = (
    datetime.datetime.fromtimestamp(CUTOFF / 1000)
    .replace(microsecond=0)
    .astimezone()
    .isoformat()
)

# -- Get version counts
print("Python versions: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PYTHON_VERSION)

versions = {}
result = resp.json()
if (
    not "aggregations" in result
    or not "2" in result.get("aggregations")
    or not "buckets" in result["aggregations"]["2"]
):
    print("No result!")
    sys.exit(-1)

buckets = result["aggregations"]["2"]["buckets"]

for bucket in buckets:
    versions[bucket["key"]] = {"instances": bucket["1"]["value"]}

# -- Get histogram
print("Histogram: Sending query for Python 2 to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PYTHON2_HISTOGRAM)
result2 = resp.json()

print("Histogram: Sending query for Python 3 to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PYTHON3_HISTOGRAM)
result3 = resp.json()


def extract_buckets(r, key, target):
    if (
        "aggregations" in r
        and "1" in r["aggregations"]
        and "buckets" in r["aggregations"]["1"]
    ):
        buckets = r["aggregations"]["1"]["buckets"]
        for bucket in buckets:
            timestamp = datetime.datetime.fromtimestamp(
                bucket["key"] // 1000
            ).astimezone()
            count = bucket["2"]["value"]

            if timestamp not in target:
                target[timestamp] = {}
            target[timestamp][key] = count


temp = {}
for key, target in (("python2", result2), ("python3", result3)):
    extract_buckets(target, key, temp)

histogram = []
for timestamp, data in temp.items():
    histogram.append(
        dict(
            start=timestamp.isoformat(),
            end=timestamp.replace(minute=59, second=59).isoformat(),
            python2=data.get("python2", 0),
            python3=data.get("python3", 0),
        )
    )

# -- Write output

with open(OUTPUT, mode="w", encoding="utf-8") as f:
    json.dump(
        {"_since": _since, "versions": versions, "histogram": histogram},
        f,
        indent=2,
        ensure_ascii=False,
    )
print("Result written to {}".format(OUTPUT))
