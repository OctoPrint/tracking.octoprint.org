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

QUERY_CORES = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.cores",
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
            "must": [
                {"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}},
                {"query_string": {"query": "event:pong"}},
            ]
        }
    },
}

QUERY_MEMORY = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.ram",
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
            "must": [
                {"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}},
                {"query_string": {"query": "event:pong"}},
            ]
        }
    },
}

QUERY_FREQUENCY = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.freq",
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
            "must": [
                {"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}},
                {"query_string": {"query": "event:pong"}},
            ]
        }
    },
}

QUERY_OS = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.os.keyword",
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
            "must": [
                {"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}},
                {"query_string": {"query": "event:pong"}},
            ]
        }
    },
}

QUERY_BITS = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.bits",
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
            "must": [
                {"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}},
                {"query_string": {"query": "event:pong"}},
            ]
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
    datetime.datetime.fromtimestamp(NOW).replace(microsecond=0).astimezone().isoformat()
)

_results = {}
_queries = (
    ("cores", QUERY_CORES),
    ("memory", QUERY_MEMORY),
    ("frequency", QUERY_FREQUENCY),
    ("os", QUERY_OS),
    ("bits", QUERY_BITS),
)

# -- Get counts


for key, query in _queries:
    print("{}: Sending query to {}".format(key, URL))
    resp = requests.post(url=URL, json=query)

    _results[key] = {}
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
        _results[key][bucket["key"]] = {"instances": bucket["1"]["value"]}

# -- Write output

with open(OUTPUT, mode="w", encoding="utf-8") as f:
    output = {
        "_since": _since,
        "_generated": _generated,
    }
    for key, data in _results.items():
        output[key] = data

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False,
    )
print("Result written to {}".format(OUTPUT))
