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

"""APRSCOT Class Definitions."""

import asyncio
import xml.etree.ElementTree as ET

from typing import Optional

import aprslib.parsing

import pytak
import aprscot

try:
    import gpsd as _gpsd
except ImportError:
    _gpsd = None


# KISS framing (RFC-less de-facto standard used by Dire Wolf & most TNCs).
FEND, FESC, TFEND, TFESC = 0xC0, 0xDB, 0xDC, 0xDD


def kiss_unescape(payload: bytes) -> bytes:
    """Reverse KISS byte-stuffing (FESC TFEND -> FEND, FESC TFESC -> FESC)."""
    out = bytearray()
    i = 0
    while i < len(payload):
        b = payload[i]
        if b == FESC and i + 1 < len(payload):
            nxt = payload[i + 1]
            out.append(FEND if nxt == TFEND else FESC if nxt == TFESC else nxt)
            i += 2
        else:
            out.append(b)
            i += 1
    return bytes(out)


def _decode_ax25_addr(frame: bytes, i: int):
    """Return (address, has_been_repeated, is_last) for the 7-byte AX.25 address at i."""
    call = "".join(chr(b >> 1) for b in frame[i : i + 6]).strip()
    ssid_byte = frame[i + 6]
    ssid = (ssid_byte >> 1) & 0x0F
    repeated = bool(ssid_byte & 0x80)  # "H" (has-been-repeated) bit
    last = bool(ssid_byte & 0x01)  # address-extension bit
    addr = call if ssid == 0 else f"{call}-{ssid}"
    return addr, repeated, last


def ax25_to_tnc2(frame: bytes):
    """Decode an AX.25 UI frame to a TNC2 monitor string (SRC>DEST,path:info).

    Returns None if the frame is too short to be a valid AX.25 UI APRS frame.
    The TNC2 string is exactly what ``aprslib.parsing.parse`` (and the APRS-IS
    path) already consume, so downstream CoT conversion is unchanged.
    """
    if len(frame) < 15:
        return None
    dest, _, _ = _decode_ax25_addr(frame, 0)
    src, _, last = _decode_ax25_addr(frame, 7)
    i = 14
    digis = []
    # Up to 8 digipeaters follow the source address (bounded to avoid a runaway
    # loop on a corrupt frame missing its address-extension bit).
    while not last and i + 7 <= len(frame) and len(digis) < 8:
        addr, repeated, last = _decode_ax25_addr(frame, i)
        digis.append(addr + ("*" if repeated else ""))
        i += 7
    if i + 2 > len(frame):  # control (UI=0x03) + PID (0xF0)
        return None
    info = frame[i + 2 :].decode("latin-1", "replace")
    path = ",".join([dest] + digis)
    return f"{src}>{path}:{info}"


class APRSWorker(pytak.QueueWorker):
    """APRS Cursor on Target Worker Class."""

    async def handle_data(self, data: bytes) -> None:
        """Handle messages from APRS Worker."""
        self._logger.debug("APRS data='%s'", data)
        frame = None

        # Skip control messages from APRS-IS:
        if b"# " in data[:2]:
            self._logger.info("APRS-IS: '%s'", data)
            return

        # Some APRS Frame types are not supported by aprslib yet:
        try:
            frame = aprslib.parsing.parse(data)
        except aprslib.exceptions.UnknownFormat:
            self._logger.warning("Unhandled APRS Frame: '%s'", data)
            return
        except aprslib.exceptions.ParseError:
            self._logger.warning("Invalid APRS Format: '%s'", data)
            return

        if not frame:
            return

        event: Optional[bytes] = aprscot.aprs_to_cot(frame, self.config)
        if not event:
            self._logger.warning("Empty CoT for APRS frame: '%s'", frame.get("raw"))
            return

        await self.put_queue(event)

    async def run(self, number_of_iterations=-1):
        """Run this Thread, Reads from Pollers."""
        self._logger.info("Running %s", self.__class__)

        aprs_host: str = self.config.get("APRS_HOST", aprscot.DEFAULT_APRSIS_HOST)
        aprs_port: str = self.config.get("APRS_PORT", aprscot.DEFAULT_APRSIS_PORT)
        if ":" in aprs_host:
            aprs_host, aprs_port = aprs_host.split(":")
        self._logger.info("Using APRS-IS server: %s:%s", aprs_host, aprs_port)

        reader, writer = await asyncio.open_connection(aprs_host, int(aprs_port))

        # APRS Parameters:
        passcode: str = self.config.get(
            "APRSIS_PASSCODE", aprscot.DEFAULT_APRSIS_PASSCODE
        )
        callsign: str = self.config.get("CALLSIGN", aprscot.DEFAULT_APRSIS_CALLSIGN)
        aprs_filter: str = self.config.get(
            "APRSIS_FILTER", aprscot.DEFAULT_APRSIS_FILTER
        )

        _login = f"user {callsign} pass {passcode} vers aprscot v8"

        if aprs_filter:
            self._logger.info("Using APRS Filter: '%s'", aprs_filter)
            _login = f"{_login} filter {aprs_filter}"
        _login = f"{_login}\r\n"

        b_login = bytes(_login, "UTF-8")
        writer.write(b_login)
        await writer.drain()

        while 1:
            data = await reader.readline()
            if data:
                await self.handle_data(data)


class KISSWorker(APRSWorker):
    """APRS-over-RF Worker: read a local KISS TNC (e.g. Dire Wolf) over TCP.

    Connects to a KISS-over-TCP server (Dire Wolf's ``KISSPORT``, default 8001),
    decodes each received AX.25 UI frame to a TNC2 string, and hands it to the
    inherited ``handle_data`` — the same CoT path as the APRS-IS worker. Enables
    fully-offline RF APRS (rtl_fm | direwolf -> aprscot -> TAK) with no APRS-IS.
    """

    async def run(self, number_of_iterations=-1):
        """Read AX.25 frames from a KISS-over-TCP TNC and convert to CoT."""
        self._logger.info("Running %s", self.__class__)

        kiss_host: str = self.config.get("KISS_HOST", "")
        kiss_port = self.config.get("KISS_PORT", aprscot.DEFAULT_KISS_PORT)
        if ":" in kiss_host:
            kiss_host, kiss_port = kiss_host.split(":")
        self._logger.info("Using KISS TNC: %s:%s", kiss_host, kiss_port)

        reader, _ = await asyncio.open_connection(kiss_host, int(kiss_port))

        buf = bytearray()
        while 1:
            chunk = await reader.read(1024)
            if not chunk:
                break  # TNC closed the connection; pytak will restart the worker.
            buf.extend(chunk)
            # KISS frames are FEND-delimited. Process every completed segment.
            while FEND in buf:
                idx = buf.index(FEND)
                segment = bytes(buf[:idx])
                del buf[: idx + 1]
                if not segment:
                    continue  # empty inter-frame segment.
                # segment = <KISS type/port byte> + escaped AX.25 frame.
                payload = kiss_unescape(segment[1:])
                tnc2 = ax25_to_tnc2(payload)
                if tnc2:
                    await self.handle_data(tnc2.encode("latin-1", "replace"))


class SensorWorker(pytak.QueueWorker):
    """Periodic sensor CoT heartbeat. Sources position from gpsd, config, or null island."""

    async def run(self, _=-1) -> None:
        period = int(self.config.get(
            "SENSOR_KEEPALIVE_PERIOD", aprscot.DEFAULT_SENSOR_KEEPALIVE_PERIOD))
        self._logger.info(
            "Running SensorWorker (period=%ds, gpsd=%s)", period, _gpsd is not None)
        while True:
            lat, lon, hae, ce, le = await self._get_position()
            cot = aprscot.gen_sensor_cot(self.config, lat, lon, hae, ce, le)
            if cot is not None:
                await self.put_queue(ET.tostring(cot))
            await asyncio.sleep(period)

    async def _get_position(self):
        if _gpsd is not None:
            try:
                result = await asyncio.to_thread(self._poll_gpsd)
                if result is not None:
                    return result
            except Exception as exc:
                self._logger.debug("gpsd unavailable: %s", exc)
        lat = float(self.config.get("SENSOR_LAT") or aprscot.DEFAULT_SENSOR_LAT)
        lon = float(self.config.get("SENSOR_LON") or aprscot.DEFAULT_SENSOR_LON)
        hae = float(self.config.get("SENSOR_HAE") or aprscot.DEFAULT_SENSOR_HAE)
        return lat, lon, hae, "9999999.0", "9999999.0"

    @staticmethod
    def _poll_gpsd():
        _gpsd.connect()
        packet = _gpsd.get_current()
        if packet.mode < 2:
            return None
        try:
            lat, lon = packet.position()
        except Exception:
            return None
        try:
            hae = packet.altitude()
        except Exception:
            hae = 0.0
        ce = str(getattr(packet, "error", {}).get("x", "9999999.0") or "9999999.0")
        le = str(getattr(packet, "error", {}).get("v", "9999999.0") or "9999999.0")
        return lat, lon, hae, ce, le
