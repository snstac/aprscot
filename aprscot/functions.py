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


def aprs_to_cot(aprs_frame: dict, cot_type: str = None, # NOQA pylint: disable=too-many-locals
                stale: int = None) -> pycot.Event:
    """Converts an APRS Frame to a Cursor-on-Target Event."""
    time = datetime.datetime.now(datetime.timezone.utc)
    cot_type = cot_type or aprscot.DEFAULT_EVENT_TYPE
    stale = stale or aprscot.DEFAULT_EVENT_STALE

    lat = aprs_frame.get("latitude")
    lon = aprs_frame.get("longitude")

    if not lat or not lon:
        return None

    callsign = aprs_frame.get("from")

    name = f"APRS.{callsign}"

    point = pycot.Point()
    point.lat = lat
    point.lon = lon

    # Circular area around the point defined by lat and lon fields in meters.
    # When used to represent error, the value represents the one sigma point
    # for a zero mean normal (Gaussian) distribution.
    point.ce = "9999999.0"

    # A height range about the event point in meters associated with the HAE
    # field. When used to represent error, the value represents the one sigma
    # point for a zero mean normal (Gaussian) distribution.
    point.le = "9999999.0"

    # Height above Ellipsoid based on WGS-84 ellipsoid (measured in meters)
    point.hae = "9999999.0"

    uid = pycot.UID()
    uid.Droid = name

    contact = pycot.Contact()
    contact.callsign = callsign

    remarks = pycot.Remarks()

    comment = aprs_frame.get("comment")
    if comment:
        remarks.value = comment

    detail = pycot.Detail()
    detail.uid = uid
    detail.contact = contact
    detail.remarks = remarks

    event = pycot.Event()
    event.version = "2.0"
    event.event_type = cot_type
    event.uid = name
    event.time = time
    event.start = time
    event.stale = time + datetime.timedelta(seconds=stale)
    # TODO: Should this be static?
    event.how = "h-g-i-g-o"
    event.point = point
    event.detail = detail

    return event


def hello_event():
    time = datetime.datetime.now(datetime.timezone.utc)
    name = 'aprscot'
    callsign = 'aprscot'

    point = pycot.Point()
    point.lat = '9999999.0'
    point.lon = '9999999.0'

    # FIXME: These values are static, should be dynamic.
    point.ce = '9999999.0'
    point.le = '9999999.0'
    point.hae = '9999999.0'

    uid = pycot.UID()
    uid.Droid = name

    contact = pycot.Contact()
    contact.callsign = callsign

    detail = pycot.Detail()
    detail.uid = uid
    detail.contact = contact

    event = pycot.Event()
    event.version = '2.0'
    event.event_type = 'a-u-G'
    event.uid = name
    event.time = time
    event.start = time
    event.stale = time + datetime.timedelta(hours=1)
    event.how = 'h-g-i-g-o'
    event.point = point
    event.detail = detail

    return event
