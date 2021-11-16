aprscot - APRS Cursor-on-Target Gateway.
****************************************

IF YOU HAVE AN URGENT OPERATIONAL NEED: Email ops@undef.net or call/sms +1-415-598-8226

.. image:: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/screenshot_1637083240_16797-50p.png
   :alt: Screenshot of APRS PLI in ATAK..
   :target: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/screenshot_1637083240_16797.png

The ``aprscot`` "APRS to Cursor On Target (COT) Gateway" transforms APRS Frames
into COT Position Location Information (PLI) Points, compatible with
Situational Awareness (SA) and Common Operating Picture (COP) applications such
as Android Team Awareness Kit (ATAK), WinTAK, RaptorX, COPERS, et al.

Features of ``aprscot``:

* Handles APRS-IS transported APRS Frames from over-the-air or Internet-based stations.
* Can transform APRS station callsign, COT Type and COT Icon for display in TAK systems.
* Can run as a service ('daemon') on any Linux system.
* Can send COT Events to any destination supported by `PyTAK <https://github.com/ampledata/pytak>`_: TLS/SSL, TCP, UDP, UDP Multicast.

See also Alan Barrow's aprstak: https://github.com/pinztrek/aprstak

Support aprscot Development
============================

aprscot has been developed for the Disaster Response, Public Safety and
Frontline community at-large. This software is currently provided at no-cost to
our end-users. All development is self-funded and all time-spent is entirely
voluntary. Any contribution you can make to further these software development
efforts, and the mission of aprscot to provide ongoing SA capabilities to our
end-users, is greatly appreciated:

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support aprscot development: Buy me a coffee!

Installation
============

The APRS to COT gateway is provided by a command-line tool called `aprscot`:

Installing as a Debian/Ubuntu Package::

    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/aprs-python/releases/latest/download/python3-aprslib_latest_all.deb
    $ sudo apt install -f ./python3-aprslib_latest_all.deb
    $ wget https://github.com/ampledata/aprscot/releases/latest/download/python3-aprscot_latest_all.deb
    $ sudo apt install -f ./python3-aprscot_latest_all.deb


Install from the Python Package Index (PyPI)::

    $ pip install aprscot


Install from this source tree::

    $ git clone https://github.com/ampledata/aprscot.git
    $ cd aprscot/
    $ python setup.py install


Usage
=====

The `aprscot` program has one command-line argument::

    $ aprscot -h
    usage: aprscot [-h] [-c CONFIG_FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE

You must create a configuration file, see `example-config.ini` in the source
repository.

An example config::

    [aprscot]
    COT_URL = tcp:takserver.example.com:8088


`APRS-IS Server-side Filter Commands <http://www.aprs-is.net/javAPRSFilter.aspx>`_ can be used::

    [aprscot]
    COT_URL = tcp:takserver.example.com:8088
    APRSIS_FILTER = f/W6PW-10/50

PLI Transforms can be created using per-station sections::

    [aprscot]
    COT_URL = tcp:takserver.example.com:8088

    [W2GMD-9]
    COT_TYPE = a-f-G-U-C
    COT_STALE = 600
    COT_NAME = Medic 52

    [NB6F-2]
    COT_NAME = Transport 2


Source
======
Github: https://github.com/ampledata/aprscot

Author
======
Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/

Copyright
=========
Copyright 2021 Greg Albrecht

`Automatic Packet Reporting System (APRS) <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR wb4apr@amsat.org

License
=======
Apache License, Version 2.0. See LICENSE for details.
