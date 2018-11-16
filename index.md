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
version. Additionally a rough location from which the request originates will be determined based on the client IP 
using the [GeoLite2 City database](https://dev.maxmind.com/geoip/geoip2/geolite2/) and 
[GeoIP](https://www.elastic.co/guide/en/logstash/current/plugins-filters-geoip.html).
The client IP address itself will **not** be tracked.

The plugin fires tracking requests for the following events. Version numbers indicate in which OctoPrint version after
1.3.10rc1 an event or additional data was added, also for as of yet unreleased versions. Most of the events can be
switched off in the settings.

  * **Regular ping every 15min**
    
    No additional recorded data.

  * **Server startup** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span>

    * OS name (e.g. "linux", "windows")
    * Python version
    * Pip version
    * Number of CPU cores, CPU frequency and RAM
    * Raspberry Pi model <span title="Only if running on a Raspberry Pi" class="label">RPi only</span>
    * OctoPi version <span title="Only if running under OctoPi" class="label">OctoPi only</span>

  * **Server shutdown** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span>
    
    No additional recorded data.

  * **Start/cancel/finish of a print job** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span>
    
    * Origin of printed file (local storage vs printer's SD card)
    * One-way SHA1 hash of the file name, unique to the instance
    * Elapsed time on print finish
    * If the system is currently throttled: current and past throttle state <span title="Only if running on a Raspberry Pi" class="label">RPi only</span> <span title="Starting with OctoPrint 1.3.10rc2" class="label label-info">1.3.10rc2+</span> 
    * If the print failed: reason of failure (cancel vs error) <span title="Starting with OctoPrint 1.3.10rc2" class="label label-info">1.3.10rc2+</span>
    
  * **Connection to a printer** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span>

    * Used serial port & baudrate
    * Firmware name as reported by `M115`

  * **Install/uninstall/enabling/disabling of a plugin** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span>

    * Plugin identifier
    * Plugin version

  * **Update of a component** <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span> 

    * Whether the update was successful or not
    * Component identifier
    * From version, to version
   
  * **System got throttled/unthrottled** <span title="Only if running on a Raspberry Pi" class="label">RPi only</span> <span title="Can be switched off in the plugin settings" class="label label-success">switchable</span> <span title="Starting with OctoPrint 1.3.10rc2" class="label label-info">1.3.10rc2+</span> 

    * Whether there's any current issue
    * Whether there's been any past issue
    * Whether there's a current undervoltage issue
    * Whether there's been a past undervoltage issue
    * Whether there's a current overheat issue
    * Whether there's been a past overheat issue

#### How and where does this data get evaluated? Are there any third parties involved?

The data gets recorded and evaluated on `tracking.octoprint.org`. It doesn't leave that server and gets evaluated in 
place through a local [ELK stack](https://www.elastic.co/elk-stack) and [Grafana](https://grafana.com/) install.

No third parties do have access to the raw data. Visualizations based on this data might be shared with the public
in the future to give a general overview over version distribution and similar metrics.

#### How can I disable tracking?

Open your OctoPrint settings, click on "Anonymous Usage Tracking", uncheck the box that says "Enable Anonymous Usage Tracking" and
save.

#### Where can I find the source of this plugin?

You can find the source code of the tracking plugin built into OctoPrint in `src/octoprint/plugins/tracking` of the 
[OctoPrint source code]({{ site.sourcerepo }}).

<center><strong>Please also see the <a href="/privacy/" rel="nofollow">Privacy Policy</a>.</strong></center>