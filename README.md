# tracking.octoprint.org scripts

Various scripts and configs used to operate the anonymous usage tracking.

  * `curator` - [curator](https://github.com/elastic/curator) config to limit data storage to 90 days max according to privacy policy
  * `dataextractor` - export scripts used for exporting to `data.octoprint.org/exports`, written in Python
  * `logstash` - [logstash](https://www.elastic.co/logstash) config for the tracking log processing
  * `nginx` - nginx config for tracking log creation
