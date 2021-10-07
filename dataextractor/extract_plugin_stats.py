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

QUERY_PLUGINS = {
    "aggs": {
        "2": {
            "terms": {
                "field": "payload.plugins.keyword",
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

QUERY_PLUGIN_VERSIONS = {
    "aggs": {
        "buckets": {
            "composite": {
                "size": 1000,
                # "after": { "plugins_and_versions": "actioncommands:0.4" },
                "sources": [
                    {
                        "plugins_and_versions": {
                            "terms": {
                                "field": "payload.plugins_and_version.keyword",
                                "order": "asc"
                            }
                        }
                    }
                ]
            },
            "aggregations": {
                "instances": {
                    "cardinality": {
                        "field": "uuid.keyword"
                    }
                }
            }
        }
    },
    "size": 0,
    "query": {
        "bool": {
            "must": [{"range": {"@timestamp": {"gte": CUTOFF, "format": "epoch_millis"}}}]
        }
    }    
}

QUERY_PLUGIN_INSTALLS = {
    "aggs": {
        "3": {
            "terms": {
                "field": "payload.plugin.keyword",
                "order": {"_count": "desc"},
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
                {
                    "query_string": {
                        "analyze_wildcard": True,
                        "query": "event:install_plugin",
                    }
                },
            ]
        }
    },
}

QUERY_PLUGIN_UNINSTALLS = {
    "aggs": {
        "3": {
            "terms": {
                "field": "payload.plugin.keyword",
                "order": {"_count": "desc"},
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
                {
                    "query_string": {
                        "analyze_wildcard": True,
                        "query": "event:uninstall_plugin",
                    }
                },
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
plugins = dict()

# -- Get accumulated plugin stats
print("Plugins: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PLUGINS)

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
    plugin = bucket["key"].lower()
    plugins[plugin] = dict(
        instances=bucket["1"]["value"],
        versions=dict(),
        install_events=0,
        uninstall_events=0,
    )

# -- Get plugin version stats
print("Plugin versions: Sending query to {}".format(URL))
after = None
count = 0

while True:
    count += 1

    query = QUERY_PLUGIN_VERSIONS.copy()
    if after is not None:
        query["aggs"]["buckets"]["composite"]["after"] = {
            "plugins_and_versions": after
        }

    print("  Query #{}, after_key: {}".format(count, after))
    resp = requests.post(url=URL, json=QUERY_PLUGIN_VERSIONS)
    result = resp.json()

    if not ("aggregations" in result and "buckets" in result.get("aggregations") and "buckets" in result.get("aggregations").get("buckets") and "after_key" in result.get("aggregations").get("buckets") and "plugins_and_versions" in result.get("aggregations").get("buckets").get("after_key")):
        break

    if len(result["aggregations"]["buckets"]["buckets"]) == 0:
        # we've gone through all buckets
        break

    after = result["aggregations"]["buckets"]["after_key"]["plugins_and_versions"]

    for bucket in result["aggregations"]["buckets"]["buckets"]:
        if not "key" in bucket or not "plugins_and_versions" in bucket["key"]:
            continue
        if not "instances" in bucket:
            continue

        plugin, version = bucket["key"]["plugins_and_versions"].rsplit(":", 1)
        if plugin in plugins:
            plugins[plugin]["versions"][version] = dict(instances=bucket["instances"]["value"])

result = resp.json()
if (
    "aggregations" in result
    and "2" in result.get("aggregations")
    and "buckets" in result["aggregations"]["2"]
):
    buckets = result["aggregations"]["2"]["buckets"]
    for bucket in buckets:
        plugin, version = bucket["key"].rsplit(":", 1)
        if plugin in plugins:
            plugins[plugin]["versions"][version] = dict(instances=bucket["1"]["value"])

# -- Get plugin installation stats
print("Install event: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PLUGIN_INSTALLS)

result = resp.json()
if (
    "aggregations" in result
    and "3" in result.get("aggregations")
    and "buckets" in result["aggregations"]["3"]
):
    buckets = result["aggregations"]["3"]["buckets"]
    for bucket in buckets:
        plugin = bucket["key"].lower()
        count = bucket["1"]["value"]

        if plugin in plugins:
            plugins[plugin]["install_events"] = count

# -- Get plugin uninstallation stats
print("Uninstall event: Sending query to {}".format(URL))
resp = requests.post(url=URL, json=QUERY_PLUGIN_UNINSTALLS)

result = resp.json()
if (
    "aggregations" in result
    and "3" in result.get("aggregations")
    and "buckets" in result["aggregations"]["3"]
):
    buckets = result["aggregations"]["3"]["buckets"]
    for bucket in buckets:
        plugin = bucket["key"].lower()
        count = bucket["1"]["value"]

        if plugin in plugins:
            plugins[plugin]["uninstall_events"] = count

with open(OUTPUT, mode="w", encoding="utf-8") as f:
    json.dump(
        dict(_since=_since, _generated=_generated, plugins=plugins),
        f,
        indent=2,
        ensure_ascii=False,
    )
print("Result written to {}".format(OUTPUT))
