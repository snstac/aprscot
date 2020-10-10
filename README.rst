aprscot - APRS Cursor-on-Target Gateway.
****************************************

.. image:: docs/screenshot2-25.png
   :alt: Screenshot of APRS points in ATAK-Div Developer Edition.
   :target: docs/screenshot2-50.png



aprscot receives APRS Frames from APRS-IS and outputs them in as
Cursor-on-Target (CoT) PLI, for use with CoT systems such as ATAK, WinTAK,
RaptorX, et al. See https://www.civtak.org/ for more information on the TAK
program.

Currently supports APRS-IS and Location-type APRS messages, and sending to TCP
CoT Hosts & TAK Servers.

Installation
============

The command-line daemon `aprscot` can be install from this source tree (A), or
from the Python Package Index (PyPI) (B).

A) To install from this source tree::

    $ git checkout https://github.com/ampledata/aprscot.git
    $ cd aprscot/
    $ python setup.py install

B) To install from PyPI::

    $ pip install aprscot


Usage
=====

The `aprscot` daemon has several runtime arguments::

    $ aprscot --help
    usage: aprscot [-h] -c CALLSIGN -C COT_HOST [-p PASSCODE] [-a APRS_HOST]
                   [-f FILTER]

    optional arguments:
      -h, --help            show this help message and exit
      -c CALLSIGN, --callsign CALLSIGN
                            APRS-IS Login Callsign
      -C COT_HOST, --cot_host COT_HOST
                            Cursor-on-Target Host or Host:Port
      -p PASSCODE, --passcode PASSCODE
                            APRS-IS Passcode
      -a APRS_HOST, --aprs_host APRS_HOST
                            APRS-IS Host (or Host:Port).
      -f FILTER, --filter FILTER
                            APRS-IS Filter, see:
                            http://www.aprs-is.net/javAPRSFilter.aspx

For minimum operation, `-c CALLSIGN` & `-C COT_HOST` are required.

The following example forwards all APRS Frames within 50 meters of W2GMD-9's
last known location to the Cursor-on-Target host at 10.1.2.3 port 4242 (TCP)::

    aprscot -c W2GMD-9 -C 10.1.2.3:4242 -f m/50


Example Cursor-on-Target Event
==============================

The `aprscot` daemon will output CoT XML Events similar to this example::

    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <event version="1.0" type="a-f-G-E-V-C" uid="APRS.W2GMD-1"
        time="2020-09-24T14:53:28.945221Z" start="2020-09-24T14:53:28.945221Z"
        stale="2020-09-24T15:53:28.945221Z" how="h-e">
       <point lat="38.51167" lon="-122.99883" hae="10" ce="10" le="10" />
    </event>


Build Status
============

Master:

.. image:: https://travis-ci.com/ampledata/aprscot.svg?branch=master
    :target: https://travis-ci.com/ampledata/aprscot

Develop:

.. image:: https://travis-ci.com/ampledata/aprscot.svg?branch=develop
    :target: https://travis-ci.com/ampledata/aprscot


Source
======
Github: https://github.com/ampledata/aprscot

Author
======
Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/

Copyright
=========
Copyright 2020 Orion Labs, Inc.

`Automatic Packet Reporting System (APRS) <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR wb4apr@amsat.org

License
=======
Apache License, Version 2.0. See LICENSE for details.

Debugging Cursor-on-Target
==========================
The publicly available ATAK source was a good reference for some of the parsing
errors the ATAK-Civ Development Build was giving me, namely `Invalid CoT
message received: Missing or invalid CoT event and/or point attributes`. Many
errors are unfortunately caught in a single try/catch block:

https://github.com/deptofdefense/AndroidTacticalAssaultKit-CIV/blob/6dc1941f45af3f9716e718dccebf42555a8c08fd/commoncommo/core/impl/cotmessage.cpp#L448

