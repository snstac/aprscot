#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Functions."""

import datetime

import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def aprs_to_cot(aprs_frame):
    """
    Converts an APRS Frame to a Cursor-on-Target Event.
    """
    lat = aprs_frame.get('latitude')
    lng = aprs_frame.get('longitude')
    if not lat or not lng:
        return

    point = pycot.Point()
    point.lat = lat
    point.lon = lng
    point.ce = '10'
    point.le = '10'
    point.hae = '10'

    event = pycot.Event()
    event.version = '1.0'
    event.event_type = 'a-f-G-E-V-C'
    event.uid = 'APRS.%s' % aprs_frame['from']
    event.time = datetime.datetime.now()
    event.how = 'h-e'
    event.point = point

    return event
