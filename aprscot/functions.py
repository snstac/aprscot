#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""APRSCOT Functions."""

import xml.etree.ElementTree as ET

from configparser import ConfigParser
from typing import Set, Union

import pytak
import aprscot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
__source__ = "https://github.com/ampledata/aprscot"


def create_tasks(
    config: ConfigParser, clitool: pytak.CLITool
) -> Set[pytak.Worker,]:
    """
    Creates specific coroutine task set for this application.

    Parameters
    ----------
    config : `ConfigParser`
        Configuration options & values.
    clitool : `pytak.CLITool`
        A PyTAK Worker class instance.

    Returns
    -------
    `set`
        Set of PyTAK Worker classes for this application.
    """
    return set([aprscot.APRSWorker(clitool.tx_queue, config)])


def aprs_to_cot_xml(
    frame: dict, config: Union[dict, None] = None
) -> Union[
    ET.Element, None
]:  # NOQA pylint: disable=too-many-locals,too-many-statements
    """Converts an APRS Frame to a Cursor-on-Target Event."""
    lat = frame.get("latitude")
    lon = frame.get("longitude")

    if not lat or not lon:
        return None

    config: dict = config or {}
    cot_stale = int(config.get("COT_STALE", pytak.DEFAULT_COT_STALE))

    callsign = frame.get("from").replace(" ", "")
    name = callsign

    cot_uid = f"APRS.{callsign}"
    cot_type = config.get("COT_TYPE", aprscot.DEFAULT_COT_TYPE)

    if "sections" in config and callsign in config.sections():
        cs_conf = config[callsign]
        cot_type = cs_conf.get("COT_TYPE", cot_type)
        cot_stale = cs_conf.get("COT_STALE", cot_stale)
        name = cs_conf.get("COT_NAME", name)
        cot_icon = cs_conf.get("COT_ICON")

    point = ET.Element("point")
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

    uid = ET.Element("UID")
    uid.set("Droid", f"{name} (APRS)")

    contact = ET.Element("contact")
    contact.set("callsign", f"{callsign} (APRS)")

    track = ET.Element("track")
    track.set("course", "9999999.0")

    detail = ET.Element("detail")
    detail.set("uid", cot_uid)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    remarks = ET.Element("remarks")

    comment = frame.get("comment")
    if comment:
        remarks.text = comment
        detail.append(remarks)

    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type)
    root.set("uid", cot_uid)
    root.set("how", "h-g-i-g-o")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(cot_stale))

    root.append(point)
    root.append(detail)

    return root


def aprs_to_cot(frame: dict, config: Union[dict, None] = None) -> Union[bytes, None]:
    """Wrapper that returns COT as an XML string."""
    cot: Union[ET.Element, None] = aprs_to_cot_xml(frame, config)
    return (
        b"\n".join([pytak.DEFAULT_XML_DECLARATION, ET.tostring(cot)]) if cot else None
    )
