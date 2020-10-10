#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Functions."""

import datetime

import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


def aprs_to_cot(aprs_frame: dict) -> pycot.Event:
    """Converts an APRS Frame to a Cursor-on-Target Event."""
    lat = aprs_frame.get('latitude')
    lon = aprs_frame.get('longitude')

    if not lat or not lon:
        return None

    # TODO: Should we make the 'APRS.' prefix configurable?
    name = 'APRS.%s' % aprs_frame.get('from')
    time = datetime.datetime.now(datetime.timezone.utc)

    point = pycot.Point()
    point.lat = lat
    point.lon = lon

    # FIXME: These values are static, should be dynamic.
    point.ce = '10'
    point.le = '10'
    point.hae = '10'

    # contact = pycot.Contact()
    # contact.callsign = name

    uid = pycot.UID()
    uid.Droid = name

    detail = pycot.Detail()
    detail.uid = uid
    # detail.contact = contact

    event = pycot.Event()
    event.version = '2.0'
    # FIXME: The 'type' is static here, should be user configurable.
    event.event_type = 'a-f-G-E-C-V'
    event.uid = name
    event.time = time
    event.start = time
    # TODO: Should this be static?
    event.stale = time + datetime.timedelta(hours=1)  # 1 hour expire
    # TODO: Should this be static?
    event.how = 'h-g-i-g-o'
    event.point = point
    event.detail = detail

    return event
