aprscot - APRS Cursor-on-Target Gateway.
****************************************

aprscot receives APRS Frames from APRS-IS and outputs them in Cursor-on-Target
XML Formatted events, for use with COT systems such as RaptorX, Falconview, etc.

Currently only supports APRS-IS and Location-type APRS messages, and only sending
to UDP COT Hosts.

More features and capabilities TK, let me know what you're looking to build!

Usage
=====

The following example forwards all APRS Frames within 100 meters of W2GMD-9's last known
location to the Cursor-on-Target host at 10.1.0.1 port 18999 (UDP)::

    aprscot -c W2GMD-9 -p xxx -C 10.1.0.1:18999 -f m/100


Example Cursor-on-Target Event
==============================

Here's what a COT message from aprscot looks like::

    <?xml version="1.0" standalone="yes" ?>
    <event version="1.0" type="a-f-G-E-V-C" uid="APRS.W2GMD-15"
           time="2017-05-24T20:53:23.059489Z" how="h-e">
      <point lat="37.693" lon="-121.72716" hae="10" ce="10" le="10" />
    </event>

Build Status
============

Master:

.. image:: https://travis-ci.org/ampledata/aprscot.svg?branch=master
    :target: https://travis-ci.org/ampledata/aprscot

Develop:

.. image:: https://travis-ci.org/ampledata/aprscot.svg?branch=develop
    :target: https://travis-ci.org/ampledata/aprscot


Source
======
Github: https://github.com/ampledata/aprscot

Author
======
Greg Albrecht W2GMD oss@undef.net

http://ampledata.org/

Copyright
=========
Copyright 2017 Greg Albrecht

`Automatic Packet Reporting System (APRS) <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR wb4apr@amsat.org

License
=======
Apache License, Version 2.0. See LICENSE for details.
