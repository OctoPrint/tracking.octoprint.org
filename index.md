---
layout: page
title: Anonymous Usage Tracking in OctoPrint
---

Starting with version 1.3.10, OctoPrint comes with a built-in plugin "Anonymous Usage Tracking" that performs anonymous 
usage tracking. Tracking will only take place if the plugin is enabled and you've decided to opt-in during initial 
setup (or enabled it manually afterwards, through the corresponding switch in the settings).

#### What data gets recorded?

All tracking requests record the OctoPrint version and a unique identifier of the OctoPrint instance (randomly created on first
start and not connected in any way to personal identifiable information) to allow counting of unique instances per 
version. Additionally the country from which the request originates will be determined based on the client IP via GeoIP.
The client IP address itself will **not** be tracked.

#### What events get tracked?

Currently the plugin fires tracking requests for the following events:

  * Server startup. Additional recorded data: 
    * OS name (e.g. "linux", "windows")
  * Start/cancel/finish of a print job. Additional recorded data: 
    * origin of printed file (local storage vs printer's SD card)
    * one-way SHA1 hash of the file name
    * elapsed time on print finish
  * Install/uninstall/enabling/disabling of a plugin. Additional recorded data: 
    * plugin identifier
    * plugin version
  * Regular ping (by default every 15min). No additional recorded data.

#### How and where does this data get evaluated? Are there any third parties involved?

The data gets recorded and evaluated on `tracking.octoprint.org`. It doesn't leave that server and gets evaluated in 
place through a local [ELK stack install](https://www.elastic.co/elk-stack).

No third parties do have access to the raw data. Visualizations based on this data might be shared with the public
in the future to give a general overview over version distribution and similar metrics.

#### How can I disable tracking?

Open your OctoPrint settings, click on "Anonymous Usage Tracking", uncheck the box that says "Enable Anonymous Usage Tracking" and
save.

#### Where can I find the source of this plugin?

You can find the source code of the tracking plugin built into OctoPrint in `src/octoprint/plugins/tracking` of the 
[OctoPrint source code]({{ site.sourcerepo }}).

<center><strong>Please also see the <a href="/privacy/" rel="nofollow">Privacy Policy</a>.</strong></center>