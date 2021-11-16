#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Functions."""

import datetime

import xml.etree.ElementTree

import pytak

import aprscot

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
__source__ = "https://github.com/ampledata/aprscot"


def aprs_to_cot_xml(aprs_frame: dict, config: dict) -> \
        [xml.etree.ElementTree, None]:  # NOQA pylint: disable=too-many-locals,too-many-statements
    """Converts an APRS Frame to a Cursor-on-Target Event."""
    time = datetime.datetime.now(datetime.timezone.utc)

    lat = aprs_frame.get("latitude")
    lon = aprs_frame.get("longitude")

    if not lat or not lon:
        return None

    callsign = aprs_frame.get("from")
    name = callsign

    if "aprscot" in config:
        aprscot_conf = config["aprscot"]
    else:
        aprscot_conf = {}

    cot_type = aprscot_conf.get("COT_TYPE", aprscot.DEFAULT_COT_TYPE)
    _cot_stale = aprscot_conf.get("COT_STALE", aprscot.DEFAULT_COT_STALE)

    if 'sections' in config and callsign in config.sections():
        cs_conf = aprscot_conf[callsign]
        cot_type = cs_conf.get("COT_TYPE", cot_type)
        _cot_stale = cs_conf.get("COT_STALE", _cot_stale)
        name = cs_conf.get("COT_NAME", name)
        cot_icon = cs_conf.get("COT_ICON")

    cot_stale = (datetime.datetime.now(datetime.timezone.utc) +
                 datetime.timedelta(
                     seconds=int(_cot_stale))).strftime(pytak.ISO_8601_UTC)

    point = xml.etree.ElementTree.Element("point")
    point.set("lat", str(lat))
    point.set("lon", str(lon))

    # Circular area around the point defined by lat and lon fields in meters.
    # When used to represent error, the value represents the one sigma point
    # for a zero mean normal (Gaussian) distribution.
    point.set("ce", "9999999.0")

    # A height range about the event point in meters associated with the HAE
    # field. When used to represent error, the value represents the one sigma
    # point for a zero mean normal (Gaussian) distribution.
    point.set("le", "9999999.0")

    # Height above Ellipsoid based on WGS-84 ellipsoid (measured in meters)
    point.set("hae", "9999999.0")

    uid = xml.etree.ElementTree.Element("UID")
    uid.set("Droid", f"{name} (APRS)")

    contact = xml.etree.ElementTree.Element("contact")
    contact.set("callsign", f"{callsign} (APRS)")

    track = xml.etree.ElementTree.Element("track")
    track.set("course", "9999999.0")

    detail = xml.etree.ElementTree.Element("detail")
    detail.set("uid", name)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    remarks = xml.etree.ElementTree.Element("remarks")

    comment = aprs_frame.get("comment")
    if comment:
        remarks.text = comment
        detail.append(remarks)

#    event.stale = time + datetime.timedelta(seconds=stale)

    root = xml.etree.ElementTree.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type)
    root.set("uid", f"APRS.{callsign}".replace(" ", ""))
    root.set("how", "h-g-i-g-o")
    root.set("time", time.strftime(pytak.ISO_8601_UTC))
    root.set("start", time.strftime(pytak.ISO_8601_UTC))
    root.set("stale", cot_stale)
    root.append(point)
    root.append(detail)

    return root


def aprs_to_cot(aprs_frame: dict, config: dict) -> str:
    """
    Converts an APRS Frame to a Cursor-on-Target Event, as a String.
    """
    cot_str: str = ""
    cot_xml: xml.etree.ElementTree = aprs_to_cot_xml(aprs_frame, config)
    if cot_xml:
        cot_str = xml.etree.ElementTree.tostring(cot_xml)
    return cot_str
