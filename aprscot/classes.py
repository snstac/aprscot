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


class _NoStatus:
    """Stand-in for pytak.StatusWriter on a pytak too old to have one.

    AryaOS boxes are updated as packages, so aprscot can land on a host whose
    pytak predates StatusWriter (added in 7.4.0; much of the fleet is still on
    7.3.13). Failing to import would take the gateway down over its telemetry
    helper, which is exactly backwards: moving CoT is the job, reporting on it
    is not.

    Degrading here is safe because it is VISIBLE. With nothing writing
    /run/aprscot/status.json, the Cockpit plugin reports "No status from this
    gateway ... may be running a pytak too old to report status" rather than
    rendering an empty feed as though the band were quiet.
    """

    def count(self, *args, **kwargs) -> None:
        return None

    def record(self, *args, **kwargs) -> None:
        return None

    def set(self, *args, **kwargs) -> None:
        return None

    def write(self, *args, **kwargs) -> bool:
        return False


# Resolved at import so a missing StatusWriter is a startup-time decision
# rather than an AttributeError on the first frame off the wire.
_StatusWriter = getattr(pytak, "StatusWriter", None)


def make_status(app_name: str, version: str):
    """Return a status writer, or a no-op if this pytak has none."""
    if _StatusWriter is None:
        return _NoStatus()
    return _StatusWriter(app_name, version=version)


# Seconds between forced status writes while the input socket is blocked in a
# read. Without this an idle-but-healthy gateway stops touching the status file
# and a reader cannot tell a quiet band from a wedged service.
STATUS_HEARTBEAT: float = 5.0

# APRS comments are short by convention but not by protocol. The status file is
# a fixed-size ring buffer by design, so the comment is clipped here rather than
# being allowed to set the file's size.
MAX_STATUS_COMMENT: int = 80


def status_fields(frame: dict, placed: bool) -> dict:
    """Fields describing one parsed APRS frame for the runtime status feed.

    ``callsign`` carries the full station identifier ("W6BSD-5") because that is
    what an operator sees on the map, and ``ssid`` repeats the suffix on its own
    because on APRS the SSID is a station-type convention (-9 mobile, -10 IGate,
    -13 weather ...) worth reading as a category rather than as part of a name.

    ``path`` is here because it is the only part of the frame that says how it
    reached us: "TCPIP*,qAC,T2SP" came off the internet feed, "WIDE1-1*" was
    heard over the air. On a box running both APRS-IS and a KISS TNC that
    distinction is the difference between a working receiver and a working
    uplink, and nothing else in the record shows it.
    """
    call = str(frame.get("from") or "")
    _, _, ssid = call.partition("-")

    path = frame.get("path") or []
    if not isinstance(path, (list, tuple)):
        path = [path]

    symbol = frame.get("symbol") or ""
    table = frame.get("symbol_table") or ""

    # aprslib puts a position frame's free text in `comment` but a status
    # beacon's in `status`. Reading only `comment` would show every status
    # beacon as a blank row, which is the majority of what a quiet APRS-IS
    # filter delivers.
    text = frame.get("comment") or frame.get("status") or ""

    return {
        "callsign": call,
        "ssid": ssid,
        # Standard two-character APRS symbol identifier (table + code).
        "symbol": f"{table}{symbol}" if symbol else "",
        "comment": str(text)[:MAX_STATUS_COMMENT],
        "path": ",".join(str(hop) for hop in path),
        # Whether this frame produced a marker. Most APRS traffic (messages,
        # telemetry, status, bulletins, queries) carries no position, so a feed
        # showing only plotted stations would sit empty on a receiver that is
        # working perfectly -- which an operator reads as a fault.
        "placed": placed,
    }


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

    def __init__(self, queue, config):
        super().__init__(queue, config)

        # Runtime status for Cockpit. Systemd gives us /run/aprscot via
        # RuntimeDirectory=, so this lands where the plugin looks for it.
        #
        # Exactly ONE writer per gateway. SensorWorker runs alongside this one
        # and deliberately does not get a StatusWriter: two writers pointed at
        # the same /run/aprscot/status.json each serialise a whole document, so
        # the file would alternate between two disjoint sets of counters and
        # the UI would flap between them once a second.
        self.status = make_status("aprscot", aprscot.__version__)

    async def _status_heartbeat(self, period: float = STATUS_HEARTBEAT) -> None:
        """Keep the status file fresh while the input socket blocks in a read.

        Runs as a side task rather than inline in the read loop, because that
        loop is parked in ``readline()``/``read()`` for as long as the band is
        quiet -- which on a filtered APRS-IS feed or a rural RF channel can be
        many minutes. A reader decides freshness from whether this file keeps
        changing, so without this an idle-but-healthy gateway is reported as
        wedged.
        """
        while True:
            await asyncio.sleep(period)
            self.status.write(force=True)

    async def handle_data(self, data: bytes) -> None:
        """Handle messages from APRS Worker."""
        self._logger.debug("APRS data='%s'", data)
        frame = None

        # Skip control messages from APRS-IS:
        if b"# " in data[:2]:
            # An APRS-IS server sends these banner/keepalive lines every ~20s
            # whether or not any station matches the filter. Counted separately
            # because they are the one signal that distinguishes "connected to
            # the server, filter is quiet" from "connection is dead" -- both of
            # which otherwise look like zero traffic from here.
            self.status.count("aprsis_keepalive")
            self.status.write()
            self._logger.info("APRS-IS: '%s'", data)
            return

        # Some APRS Frame types are not supported by aprslib yet:
        try:
            frame = aprslib.parsing.parse(data)
        except aprslib.exceptions.UnknownFormat:
            # Deliberately NOT counted as rx. An undecodable line is not an
            # APRS frame we heard, and folding it into rx would let a garbled
            # RF feed read as healthy traffic.
            self.status.count("unknown_format")
            self.status.write()
            self._logger.warning("Unhandled APRS Frame: '%s'", data)
            return
        except aprslib.exceptions.ParseError:
            self.status.count("parse_error")
            self.status.write()
            self._logger.warning("Invalid APRS Format: '%s'", data)
            return

        if not frame:
            self.status.count("empty_frame")
            self.status.write()
            return

        self.status.count("rx")

        event: Optional[bytes] = aprscot.aprs_to_cot(frame, self.config)

        # Record EVERY parsed frame, not just the ones that produce a marker.
        # See status_fields(): positionless APRS is the majority of the band.
        self.status.record(**status_fields(frame, placed=event is not None))

        if not event:
            # The COMMON case, not an error. This was logged at WARNING, which
            # meant a healthy gateway filled the journal with warnings about
            # ordinary APRS messages and telemetry; the count is the honest
            # place for it.
            self.status.count("no_position")
            self.status.write()
            self._logger.debug("No position in APRS frame: '%s'", frame.get("raw"))
            return

        self.status.count("emitted")
        self.status.write()
        await self.put_queue(event)

    async def run(self, number_of_iterations=-1):
        """Run this Thread, Reads from Pollers."""
        self._logger.info("Running %s", self.__class__)

        aprs_host: str = self.config.get("APRS_HOST", aprscot.DEFAULT_APRSIS_HOST)
        aprs_port: str = self.config.get("APRS_PORT", aprscot.DEFAULT_APRSIS_PORT)
        if ":" in aprs_host:
            aprs_host, aprs_port = aprs_host.split(":")
        self._logger.info("Using APRS-IS server: %s:%s", aprs_host, aprs_port)

        # Write BEFORE connecting. If APRS-IS is unreachable this worker dies
        # and systemd restarts it every 20s, and with no status file at all the
        # UI can only say "no status", which is indistinguishable from aprscot
        # having failed to start. Publishing connected=False says which.
        self.status.set(source=f"aprsis://{aprs_host}:{aprs_port}", connected=False)
        self.status.write(force=True)

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

        self.status.set(connected=True, aprs_filter=aprs_filter or "")
        self.status.write(force=True)

        heartbeat = asyncio.ensure_future(self._status_heartbeat())
        try:
            while 1:
                data = await reader.readline()
                if data:
                    await self.handle_data(data)
        finally:
            heartbeat.cancel()


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

        # See APRSWorker.run(): published before the connect attempt so a TNC
        # that is not listening reads as "aprscot up, TNC down" rather than as
        # aprscot itself being absent.
        self.status.set(source=f"kiss://{kiss_host}:{kiss_port}", connected=False)
        self.status.write(force=True)

        reader, _ = await asyncio.open_connection(kiss_host, int(kiss_port))

        self.status.set(connected=True)
        self.status.write(force=True)

        heartbeat = asyncio.ensure_future(self._status_heartbeat())
        buf = bytearray()
        try:
            while 1:
                chunk = await reader.read(1024)
                if not chunk:
                    break  # TNC closed the connection; pytak restarts the worker.
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
                    else:
                        # Short or corrupt AX.25 -- routine on a noisy channel,
                        # and counted rather than logged so a marginal RF path
                        # is visible as a ratio instead of as journal spam.
                        self.status.count("bad_ax25")
                        self.status.write()
        finally:
            heartbeat.cancel()


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
