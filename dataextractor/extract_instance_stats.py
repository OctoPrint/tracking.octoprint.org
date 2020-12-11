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
CUTOFF = int(
    datetime.datetime.fromtimestamp(NOW - DAYS * 24 * 60 * 60).timestamp() * 1000
)
CUTOFF_HISTOGRAM = int(
    datetime.datetime.fromtimestamp(NOW - DAYS * 24 * 60 * 60)
    .replace(minute=0, second=0, microsecond=0)
    .timestamp()
    * 1000
)


QUERY_INSTANCE_COUNT = {
    "aggs": {"1": {"cardinality": {"field": "uuid.keyword"}}},
    "size": 0,
    "query": {
        "bool": {
            "must": [{"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}}]
        }
    },
}

QUERY_VERSION = {
    "aggs": {
        "2": {
            "terms": {
                "field": "octoprint_version.keyword",
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

QUERY_INSTANCE_HISTOGRAM = {
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                {
                    "range": {
                        "@timestamp": {"gte": CUTOFF_HISTOGRAM, "format": "epoch_millis"}
                    }
                },
                {"query_string": {"analyze_wildcard": True, "query": "*"}},
            ]
        }
    },
    "aggs": {
        "1": {
            "date_histogram": {
                "interval": "1h",
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
_generated = (
    datetime.datetime.fromtimestamp(NOW / 1000)
    .replace(microsecond=0)
    .astimezone()
    .isoformat()
)

output = dict(_since=_since, _generated=_generated)

# -- Get instance count
print("Instance count: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_INSTANCE_COUNT)

result = resp.json()
if (
    not "aggregations" in result
    or not "1" in result.get("aggregations")
    or not "value" in result["aggregations"]["1"]
):
    print("No result!")
    sys.exit(-1)

output["count"] = result["aggregations"]["1"]["value"]

# -- Version count
print("Instance versions: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_VERSION)

versions = dict()
result = resp.json()
if (
    "aggregations" in result
    and "2" in result.get("aggregations")
    and "buckets" in result["aggregations"]["2"]
):
    buckets = result["aggregations"]["2"]["buckets"]
    for bucket in buckets:
        version = bucket["key"]
        versions[version] = bucket["1"]["value"]
output["versions"] = versions

# -- Histogram
print("Histogram: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_INSTANCE_HISTOGRAM)

histogram = list()
result = resp.json()
if (
    "aggregations" in result
    and "1" in result.get("aggregations")
    and "buckets" in result["aggregations"]["1"]
):
    buckets = result["aggregations"]["1"]["buckets"]
    for bucket in buckets:
        timestamp = datetime.datetime.fromtimestamp(bucket["key"] // 1000).astimezone()
        count = bucket["2"]["value"]

        histogram.append(
            dict(
                start=timestamp.isoformat(),
                end=timestamp.replace(minute=59, second=59).isoformat(),
                count=count,
            )
        )
output["histogram"] = histogram

with open(OUTPUT, mode="w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("Result written to {}".format(OUTPUT))
