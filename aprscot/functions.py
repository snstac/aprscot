#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Functions."""

import datetime

import aprs
import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def decode_lat_lon(lat_lng: str) -> tuple:
    """
    Decodes APRS DMS Lat/Lng into Decimal Lat/Lng.
    """
    lat_lon = (None, None)

    try:
        ll_match = aprscot.LL_REX.search(lat_lng)
    finally:
        pass

    if ll_match is not None:
        aprs_lat = ll_match.group('aprs_lat')
        aprs_lat_hours = int(aprs_lat[:2])
        aprs_lat_mins = float(aprs_lat[-5:])
        decimal_lat = aprs.decimaldegrees.dm2decimal(
            aprs_lat_hours, aprs_lat_mins
        )

        aprs_lng = ll_match.group('aprs_lng')
        aprs_lng_hours = int(aprs_lng[:3])
        aprs_lng_mins = float(aprs_lng[-5:])
        decimal_lng = aprs.decimaldegrees.dm2decimal(
            aprs_lng_hours, aprs_lng_mins
        )

        lat_lon = decimal_lat, decimal_lng

    return lat_lon


def aprs_to_cot(aprs_frame: aprs.Frame) -> pycot.Event:
    """
    Converts an APRS Frame to a Cursor-on-Target Event.

    :param aprs_frame: An `aprs.Frame` APRS Frame Object.
    :type aprs_frame: `aprs.Frame`
    """
    lat, lon = decode_lat_lon(str(aprs_frame.info))
    if lat is None or lon is None:
        return None

    time = datetime.datetime.now()

    point = pycot.Point()
    point.lat = lat
    point.lon = f'-{str(lon)}'  # TODO: Western Hemisphere Only?
    point.ce = '10'
    point.le = '10'
    point.hae = '10'

    event = pycot.Event()
    event.version = '1.0'
    event.event_type = 'a-f-G-E-V-C'
    event.uid = 'APRS.%s' % aprs_frame.source
    event.time = time
    event.start = time
    event.stale = time + + datetime.timedelta(hours=1)  # 1 hour expire
    event.how = 'h-e'
    event.point = point

    return event
