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

Currently the plugin fires tracking requests for the following events, most of which can be disabled in the plugin's settings:

  * **Regular ping every 15min**. No additional recorded data.

  * **Server startup**. Can be disabled in the plugin's settings. Additional recorded data: 
    * OS name (e.g. "linux", "windows")
    * Python version
    * Pip version
    * Number of CPU cores, CPU frequency and RAM
    * If running on a Raspberry Pi: Raspberry Pi model
    * If running on OctoPi: OctoPi version

  * **Server shutdown**. Can be disabled in the plugin's settings. No additional recorded data.

  * **Start/cancel/finish of a print job**. Can be disabled in the plugin's settings. Additional recorded data: 
    * Origin of printed file (local storage vs printer's SD card)
    * One-way SHA1 hash of the file name, unique to the instance
    * Elapsed time on print finish
    * If the system is currently throttled (currently only detected on Raspberry Pis): current and past throttle state
    
  * **Connection to a printer**. Can be disabled in the plugin's settings. Additional recorded data:
    * Used serial port & baudrate
    * Firmware name as reported by `M115`

  * **Install/uninstall/enabling/disabling of a plugin**. Can be disabled in the plugin's settings. Additional recorded data: 
    * Plugin identifier
    * Plugin version

  * **Update of a component** (e.g. OctoPrint itself or a third party plugin). Can be disabled in the plugin's settings. Additional recorded data:
    * Whether the update was successful or not
    * Component identifier
    * From version, to version
   
  * **System got throttled/unthrottled** (e.g. due to undervoltage or overheat, currently only detected on Raspberry Pis). Can be disabled in the plugin's settings. Additional recorded data:
    * Whether there's any current issue
    * Whether there's been any past issue
    * Whether there's a current undervoltage issue
    * Whether there's been a past undervoltage issue
    * Whether there's a current overheat issue
    * Whether there's been a past overheat issue

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