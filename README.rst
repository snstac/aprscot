aprscot - APRS Cursor-on-Target Gateway.
****************************************

.. image:: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/screenshot_1637083240_16797-50p.png
   :alt: Screenshot of APRS PLI in ATAK.
   :target: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/screenshot_1637083240_16797.png

The APRS to Cursor On Target Gateway (APRSCOT) provides beyond line-of-sight 
blue force tracking capabilities using commercial off the shelf components. 
This gateway uses the Automatic Packet Reporting System (APRS) and APRS-IS 
network to forward APRS position reports to Cursor On Target (COT) clients 
such as the Android Team Awareness Kit (ATAK), WinTAK, et al. Other 
situational awareness & common operating picture platforms are supported 
through use of COT, such as TAKX & COPERS.

APRS Frames can also be transformed or callsigns normalized before forwarding 
as COT.  Almost any network destination is available, including TCP & UDP 
Mulitcast.

Features of ``aprscot``:

* Handles APRS-IS transported APRS Frames from over-the-air or Internet-based stations.
* Can transform APRS station callsign, COT Type and COT Icon for display in TAK systems.
* Can run as a service ('daemon') on any Linux system.
* Can send COT Events to any destination supported by `PyTAK <https://github.com/ampledata/pytak>`_: TLS/SSL, TCP, UDP, UDP Multicast.

See also:

* Hayt's `APRS-TAK ATAK Plugin <https://drive.google.com/drive/folders/1o8tsalgxUGxdg2HiDw5xVu_-bnr63F3d>`_
* Alan Barrow's aprstak: https://github.com/pinztrek/aprstak

Concept:

.. image:: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/aprscot-concept.png
   :alt: APRSCOT concept diagram.
   :target: https://raw.githubusercontent.com/ampledata/aprscot/main/docs/aprscot-concept.png


Support Development
===================

**Tech Support**: Email support@undef.net or Signal/WhatsApp: +1-310-621-9598

This tool has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to users. Any contribution you can make to further this project's development
efforts is greatly appreciated.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support Development: Buy me a coffee!


Installation
============

The APRS to COT gateway is service started with a command-line tool 
called ``aprscot``. There are three options for installing ``aprscot``, in order 
preferred option they are:

**Option I: Install as a Debian / Ubuntu Package**::

    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/aprs-python/releases/latest/download/python3-aprslib_latest_all.deb
    $ sudo apt install -f ./python3-aprslib_latest_all.deb
    $ wget https://github.com/ampledata/aprscot/releases/latest/download/python3-aprscot_latest_all.deb
    $ sudo apt install -f ./python3-aprscot_latest_all.deb


Option II: Install from the Python Package Index (PyPI)::

    $ python3 -m pip install aprscot


Option III: Install from this source tree::

    $ git clone https://github.com/ampledata/aprscot.git
    $ cd aprscot/
    $ python3 setup.py install


Usage
=====

The ``aprscot`` program has one command-line argument::

    $ aprscot -h
    usage: aprscot [-h] [-c CONFIG_FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE

You must create a configuration file, see ``example-config.ini`` in the source
repository.

An example config, ``COT_URL`` is our COT destination server or client::

    [aprscot]
    COT_URL = tcp://takserver.example.com:8088


`APRS-IS Server-side Filter Commands <http://www.aprs-is.net/javAPRSFilter.aspx>`_ 
can be used to filter incoming APRS Frames::

    [aprscot]
    COT_URL = tcp:takserver.example.com:8088
    APRSIS_FILTER = f/W6PW-10/50

PLI Transforms can be created using per-station sections. In this example, 
we're overriding ``W2GMD-9``'s COT Type & Callsign, and ``NB6F-2``'s Callsign::

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

* APRSCOT is Copyright 2022 Greg Albrecht <oss@undef.net>
* `Automatic Packet Reporting System (APRS) <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR (SK) wb4apr@amsat.org


License
=======

Copyright 2022 Greg Albrecht <oss@undef.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
