#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Functions."""

import datetime

import aprs
import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def decode_ll(lat_lng):
    """
    Decodes APRS DMS Lat/Lng into Decimal Lat/Lng.
    """
    ll_match = aprscot.LL_REX.search(lat_lng)

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

        return decimal_lat, decimal_lng


def aprs_to_cot(aprs_frame):
    """
    Converts an APRS Frame to a Cursor-on-Target Event.

    :param aprs_frame: An `aprs.Frame` APRS Frame Object.
    :type aprs_frame: `aprs.Frame`
    """
    decoded_ll = decode_ll(aprs_frame.text)
    if decoded_ll is None:
        return

    point = pycot.Point()
    point.lat = decoded_ll[0]
    point.lon = '-' + str(decoded_ll[1])
    point.ce = '10'
    point.le = '10'
    point.hae = '10'

    event = pycot.Event()
    event.version = '1.0'
    event.event_type = 'a-f-G-E-V-C'
    event.uid = 'APRS.%s' % aprs_frame.source
    event.time = datetime.datetime.now()
    event.how = 'h-e'
    event.point = point

    return event
