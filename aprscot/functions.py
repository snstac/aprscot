#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""APRSCOT Functions."""

import xml.etree.ElementTree as ET

from configparser import ConfigParser, SectionProxy
from typing import Set, Union

import pytak
import aprscot


def sensor_beacon_enabled(config: Union[dict, SectionProxy]) -> bool:
    """Return whether the periodic receiver beacon is enabled."""
    value = config.get("SENSOR_BEACON", "1")
    return str(value).strip().lower() not in {"0", "false", "no", "off"}


def create_tasks(config: ConfigParser, clitool: pytak.CLITool) -> Set[pytak.Worker,]:
    """
    Create a specific coroutine task set for this application.

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
    # Input transport: a local KISS TNC (Dire Wolf, offline RF) when KISS_HOST is
    # set, otherwise the APRS-IS internet feed. Both emit CoT via the same path.
    if config.get("KISS_HOST"):
        tasks = set([aprscot.KISSWorker(clitool.tx_queue, config)])
    else:
        tasks = set([aprscot.APRSWorker(clitool.tx_queue, config)])
    if sensor_beacon_enabled(config):
        tasks.add(aprscot.SensorWorker(clitool.tx_queue, config))
    return tasks


def aprs_to_cot_xml(
    frame: dict, config: Union[dict, None] = None
) -> Union[
    ET.Element, None
]:  # NOQA pylint: disable=too-many-locals,too-many-statements
    """Convert an APRS Frame to a Cursor on Target Event."""
    lat = frame.get("latitude")
    lon = frame.get("longitude")
    afrom = frame.get("from")

    if not lat or not lon or not afrom:
        return None

    config = config or {}
    cot_stale = int(config.get("COT_STALE", aprscot.DEFAULT_COT_STALE))

    callsign = afrom.replace(" ", "")
    name = callsign

    cot_uid = f"APRS.{callsign}"
    cot_type = config.get("COT_TYPE", aprscot.DEFAULT_COT_TYPE)
    cot_icon = config.get("COT_ICON")

    if "sections" in config and callsign in config.sections():
        cs_conf = config[callsign]
        cot_type = cs_conf.get("COT_TYPE", cot_type)
        cot_stale = cs_conf.get("COT_STALE", cot_stale)
        name = cs_conf.get("COT_NAME", name)
        cot_icon = cs_conf.get("COT_ICON")

    contact = ET.Element("contact")
    contact.set("callsign", f"{callsign} (APRS)")

    track = ET.Element("track")
    track.set("course", "9999999.0")

    detail = ET.Element("detail")
    detail.append(contact)
    detail.append(track)

    if cot_icon:
        usericon = ET.Element("usericon")
        usericon.set("iconsetpath", cot_icon)
        detail.append(usericon)

    remarks = ET.Element("remarks")

    comment = frame.get("comment")
    if comment:
        remarks.text = comment
        detail.append(remarks)

    # CE
    # Circular area around the point defined by lat and lon fields in meters.
    # When used to represent error, the value represents the one sigma point
    # for a zero mean normal (Gaussian) distribution.
    #
    # LE
    # A height range about the event point in meters associated with the HAE
    # field. When used to represent error, the value represents the one sigma
    # point for a zero mean normal (Gaussian) distribution.
    #
    # HAE
    # Height above Ellipsoid based on WGS-84 ellipsoid (measured in meters)

    cot_d = {
        "lat": str(lat),
        "lon": str(lon),
        "ce": "9999999.0",
        "le": "9999999.0",
        "hae": "9999999.0",
        "uid": cot_uid,
        "cot_type": cot_type,
        "stale": cot_stale,
    }

    cot = pytak.gen_cot_xml(**cot_d)
    cot.set("access", config.get("COT_ACCESS", pytak.DEFAULT_COT_ACCESS))

    _detail = cot.findall("detail")[0]
    flowtags = _detail.findall("_flow-tags_")
    detail.extend(flowtags)
    cot.remove(_detail)
    cot.append(detail)

    return cot


def aprs_to_cot(frame: dict, config: Union[dict, None] = None) -> Union[bytes, None]:
    """Wrapper that returns COT as an XML string."""
    cot: Union[ET.Element, None] = aprs_to_cot_xml(frame, config)
    return (
        b"\n".join([pytak.DEFAULT_XML_DECLARATION, ET.tostring(cot)]) if cot else None
    )


def gen_sensor_cot(
    config=None, lat: float = 0.0, lon: float = 0.0, hae: float = 0.0,
    ce: str = "9999999.0", le: str = "9999999.0",
):
    """Generate a periodic sensor beacon CoT (a-f-G-E-S-E)."""
    config = config or {}
    sensor_id = config.get("SENSOR_ID", aprscot.DEFAULT_SENSOR_ID)
    cot_type = config.get("SENSOR_COT_TYPE", aprscot.DEFAULT_SENSOR_COT_TYPE)
    cot_stale = int(config.get("COT_STALE", pytak.DEFAULT_COT_STALE))
    callsign = config.get("SENSOR_CALLSIGN", sensor_id)
    payload_type = config.get("SENSOR_PAYLOAD_TYPE", aprscot.DEFAULT_SENSOR_PAYLOAD_TYPE)

    contact = ET.Element("contact")
    contact.set("callsign", callsign)

    sensor_elem = ET.Element("sensor")
    sensor_elem.set("sensor_id", sensor_id)
    sensor_elem.set("type", payload_type)

    detail = ET.Element("detail")
    detail.append(contact)
    detail.append(sensor_elem)

    cot = pytak.gen_cot_xml(
        lat=str(lat), lon=str(lon), hae=str(hae), ce=ce, le=le,
        uid=f"SENSOR.{sensor_id}", cot_type=cot_type, stale=cot_stale,
    )
    cot.set("how", "m-g")
    cot.set("access", config.get("COT_ACCESS", pytak.DEFAULT_COT_ACCESS))
    _detail = cot.find("detail")
    if _detail is not None:
        cot.remove(_detail)
    cot.append(detail)
    return cot
