# Diana Extras

This repository contains a collection of tools for use with Diana, a meteorological workstation
(http://diana.met.no). Diana does not need any of these tools to function; they are supplied
to bridge the gap between the file formats and systems supported by Diana and those used by
other tools and systems.

CAP_to_KML
----------
The `cap2kml.py` tool is used to convert Common Alerting Protocol (CAP) messages that contain
polygons into KML files for visualisation in Diana.

LLF_to_KML
----------
The `llf2kml.py` tool is used to convert Low Level Forecast (LLF) messages into KML files for
visualisation in Diana.

bdiana-extras
-------------
The `bdiana-waiter.py` script is used to run bdiana for each input file copied to a specified
input directory. The input files are deleted afterwards.

References
----------

* Diana: http://diana.met.no
* Common Alerting Protocol (CAP) 1.2: http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html
