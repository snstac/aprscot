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

See also Alan Barrow's aprstak: https://github.com/pinztrek/aprstak

Installation
============

The command-line daemon `aprscot` can be install from this source tree (A), or
from the Python Package Index (PyPI) (B).

A) To install from this source tree::

    $ git clone https://github.com/ampledata/aprscot.git
    $ cd aprscot/
    $ python setup.py install

B) To install from PyPI::

    $ pip install aprscot


Usage
=====

The `aprscot` daemon has several runtime arguments::

    $ aprscot --help
      usage: aprscot [-h] -U COT_URL [-K FTS_TOKEN] [-S COT_STALE] -c CALLSIGN
                     [-p PASSCODE] [-a APRS_HOST] [-f APRS_FILTER]

      optional arguments:
        -h, --help            show this help message and exit
        -U COT_URL, --cot_url COT_URL
                              URL to CoT Destination.
        -K FTS_TOKEN, --fts_token FTS_TOKEN
                              FreeTAKServer REST API Token.
        -S COT_STALE, --cot_stale COT_STALE
                              CoT Stale period, in seconds
        -c CALLSIGN, --callsign CALLSIGN
                              APRS-IS Login Callsign
        -p PASSCODE, --passcode PASSCODE
                              APRS-IS Passcode
        -a APRS_HOST, --aprs_host APRS_HOST
                              APRS-IS Host (or Host:Port).
        -f APRS_FILTER, --aprs_filter APRS_FILTER
                              APRS-IS Filter, see: http://www.aprs-
                              is.net/javAPRSFilter.aspx


The following example forwards all APRS Frames within 50 meters of W2GMD-9's
last known location to the Cursor-on-Target host at 10.1.2.3 port 8087 (TCP)::

    aprscot -c W2GMD-9 -U tcp:10.1.2.3:8087 -f 'm/50'

Build Status
============

.. image:: https://travis-ci.com/ampledata/aprscot.svg?branch=main
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
