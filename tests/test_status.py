#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com
# SPDX-License-Identifier: Apache-2.0

"""Tests for the APRSCOT runtime status surface (/run/aprscot/status.json).

The frames below are real TNC2 strings, and which of them aprslib can parse is
load-bearing rather than incidental: aprslib raises UnknownFormat for telemetry
and station-capability packets, which are a large share of a live APRS-IS feed.
A status surface written against imagined traffic would report a gateway that
does not exist.

These drive the coroutines with ``asyncio.run()`` rather than pytest-asyncio,
which is NOT installed in this environment. Written as bare ``async def`` tests
pytest silently SKIPS them while still counting them as collected -- tests that
cannot fail.
"""

import asyncio
import json
import logging

import pytest

import pytak

from aprscot import classes
from aprscot.classes import MAX_STATUS_COMMENT, APRSWorker, KISSWorker

HAS_STATUS_WRITER = hasattr(pytak, "StatusWriter")

requires_status_writer = pytest.mark.skipif(
    not HAS_STATUS_WRITER,
    reason="installed pytak has no StatusWriter (added in 7.4.0)",
)

# --- real frames ---------------------------------------------------------

# Weather station with a position: parses, plots.
FRAME_WX_POSITION = (
    b"SUNSET>APRS,TCPIP*,qAC,T2SP:@145502z3745.60N/12229.85W_000/"
    b"000g000t060P000h99b00030W2GMD Outer Sunset, SF IGate/Digipeater "
    b"http://w2gmd.org"
)

# Mobile station heard over RF via two digipeaters. The path is what says so.
FRAME_RF_POSITION = (
    b"W2GMD-9>APRS,WIDE1-1*,WIDE2-1:!3746.00N/12225.00W>Mobile de W2GMD"
)

# Status beacon: parses cleanly, carries no position. The common case.
FRAME_STATUS = b"W2GMD-1>APRS,TCPIP*,qAC,T2SP:>Monitoring 146.52 simplex"

# Telemetry. aprslib does not support this format -> UnknownFormat.
FRAME_TELEMETRY = b"W6BSD-5>APDW15,TCPIP*,qAC,T2CAWEST:T#243,180,41856,487,0,0,00000000"

# Station capabilities. Also UnknownFormat.
FRAME_CAPABILITIES = (
    b"AE6DC-5>APDW15,TCPIP*,qAC,T2VAN:<IGATE,MSG_CNT=35,PKT_CNT=7,DIR_CNT=3"
)

# Not an APRS packet at all -> ParseError.
FRAME_GARBAGE = b"this is not aprs"

# An APRS-IS server banner/keepalive line, not a frame.
APRSIS_KEEPALIVE = b"# aprsc 2.1.10-gcaa1c8f 1 Aug 2026 00:00:00 GMT T2SP"

LONG_COMMENT = b"X" * 200
FRAME_LONG_COMMENT = b"W2GMD>APRS,TCPIP*:!3746.00N/12225.00W>" + LONG_COMMENT


async def _noop_put(event):
    return None


@requires_status_writer
class TestStatusSurface:
    """What the Cockpit plugin reads, asserted against real frames."""

    def _worker(self, tmp_path, status=None):
        worker = APRSWorker.__new__(APRSWorker)
        worker.config = {}
        worker._logger = logging.getLogger("test")
        worker.status = status or pytak.StatusWriter(
            "aprscot-test", path=str(tmp_path / "status.json")
        )
        worker.put_queue = _noop_put
        return worker

    def _handle(self, worker, raw):
        asyncio.run(worker.handle_data(raw))

    def _doc(self, worker):
        with open(worker.status.path) as handle:
            return json.load(handle)

    def test_position_frame_is_emitted_and_marked_placed(self, tmp_path):
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_WX_POSITION)

        doc = self._doc(worker)
        assert doc["counters"]["rx"] == 1
        assert doc["counters"]["emitted"] == 1
        entry = doc["recent"][0]
        assert entry["callsign"] == "SUNSET"
        assert entry["placed"] is True
        assert entry["symbol"] == "/_"  # weather station

    def test_positionless_frame_still_appears_in_the_feed(self, tmp_path):
        """The point of showing decodes rather than only plotted stations.

        A status beacon is a perfectly good decode and proof the receiver
        works, but it plots nothing. A plotted-only feed would sit empty on a
        healthy gateway, which an operator reads as a fault.
        """
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_STATUS)

        doc = self._doc(worker)
        assert doc["counters"]["rx"] == 1
        assert doc["counters"]["no_position"] == 1
        assert "emitted" not in doc["counters"]
        entry = doc["recent"][0]
        assert entry["callsign"] == "W2GMD-1"
        assert entry["placed"] is False
        # aprslib files status text under `status`, not `comment`; reading only
        # `comment` would render every status beacon as a blank row.
        assert entry["comment"] == "Monitoring 146.52 simplex"

    @pytest.mark.parametrize("frame", [FRAME_TELEMETRY, FRAME_CAPABILITIES])
    def test_unparseable_frame_is_not_counted_as_received(self, tmp_path, frame):
        """A format aprslib cannot decode is not traffic we heard.

        Folding these into `rx` would let a garbled RF feed -- or an APRS-IS
        filter delivering nothing but telemetry -- read as healthy traffic.
        """
        worker = self._worker(tmp_path)
        self._handle(worker, frame)

        doc = self._doc(worker)
        assert doc["counters"]["unknown_format"] == 1
        assert "rx" not in doc["counters"]
        assert doc["recent"] == []

    def test_garbage_is_counted_as_a_parse_error_not_as_traffic(self, tmp_path):
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_GARBAGE)

        doc = self._doc(worker)
        assert doc["counters"]["parse_error"] == 1
        assert "rx" not in doc["counters"]
        assert doc["recent"] == []

    def test_aprsis_keepalive_is_counted_but_is_not_a_contact(self, tmp_path):
        """The one signal separating "quiet filter" from "dead connection"."""
        worker = self._worker(tmp_path)
        self._handle(worker, APRSIS_KEEPALIVE)

        doc = self._doc(worker)
        assert doc["counters"]["aprsis_keepalive"] == 1
        assert "rx" not in doc["counters"]
        assert doc["recent"] == []

    def test_ssid_is_broken_out_of_the_callsign(self, tmp_path):
        """SSID is a station-type convention (-9 mobile), worth its own field."""
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_RF_POSITION)

        entry = self._doc(worker)["recent"][0]
        assert entry["callsign"] == "W2GMD-9"
        assert entry["ssid"] == "9"

    def test_path_distinguishes_rf_from_aprsis(self, tmp_path):
        """On a box running both inputs this is the only field that tells you
        whether the receiver or the uplink is doing the work."""
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_RF_POSITION)
        self._handle(worker, FRAME_WX_POSITION)
        # Writes are rate-limited to 1/s by design; the run loop's heartbeat is
        # what reconciles the file. Forcing here stands in for that heartbeat.
        worker.status.write(force=True)

        paths = [entry["path"] for entry in self._doc(worker)["recent"]]
        assert paths == ["WIDE1-1*,WIDE2-1", "TCPIP*,qAC,T2SP"]

    def test_comment_is_clipped_so_the_file_stays_bounded(self, tmp_path):
        worker = self._worker(tmp_path)
        self._handle(worker, FRAME_LONG_COMMENT)

        comment = self._doc(worker)["recent"][0]["comment"]
        assert len(comment) == MAX_STATUS_COMMENT
        assert len(LONG_COMMENT) > MAX_STATUS_COMMENT  # the clip really happened

    def test_kiss_run_publishes_status_around_the_connect(self, tmp_path):
        """Exercise run() itself against a real loopback TNC.

        The unit tests above drive handle_data() directly, which would still
        pass if the startup write and heartbeat were never wired into run() at
        all -- and that wiring is precisely what makes a silent-but-healthy
        gateway distinguishable from a dead one.
        """
        worker = self._worker(tmp_path)

        # Hold the writer: from Python 3.13 StreamWriter.__del__ closes the
        # transport, so a handler that drops its reference hangs up instantly
        # and the worker sees EOF rather than an idle TNC.
        clients = []

        async def serve(reader, writer):
            clients.append(writer)
            await reader.read()

        async def drive():
            server = await asyncio.start_server(serve, "127.0.0.1", 0)
            port = server.sockets[0].getsockname()[1]
            worker.config = {"KISS_HOST": "127.0.0.1", "KISS_PORT": str(port)}
            task = asyncio.ensure_future(KISSWorker.run(worker))
            await asyncio.sleep(0.1)
            # Read while the worker is still up. run()'s exit path deliberately
            # rewrites connected=false to flush the final counters.
            doc = self._doc(worker)
            task.cancel()
            server.close()
            return port, doc

        port, doc = asyncio.run(drive())

        assert doc["source"] == f"kiss://127.0.0.1:{port}"
        assert doc["connected"] is True

    def test_heartbeat_writes_status_with_no_traffic_at_all(self, tmp_path):
        """An idle gateway must still prove it is alive.

        Without this the status file never appears on a quiet band, and "no
        status" is indistinguishable from "aprscot failed to start".
        """
        worker = self._worker(tmp_path)

        async def drive():
            task = asyncio.ensure_future(worker._status_heartbeat(period=0.01))
            await asyncio.sleep(0.05)
            task.cancel()

        asyncio.run(drive())

        doc = self._doc(worker)
        assert doc["counters"] == {}  # nothing was received
        assert doc["wall_t"] > 0  # but the file is being kept fresh


class TestStatusDegradesVisibly:
    """A pytak without StatusWriter must not take the gateway down.

    The fleet runs pytak 7.3.13, which has no StatusWriter at all.
    """

    def test_no_op_status_when_pytak_is_too_old(self, monkeypatch):
        monkeypatch.setattr(classes, "_StatusWriter", None)
        status = classes.make_status("aprscot", "0.0.0")

        assert isinstance(status, classes._NoStatus)
        # Every call the worker makes must be safe on the stand-in.
        status.count("rx")
        status.record(callsign="W2GMD")
        status.set(connected=True)
        assert status.write() is False

    def test_data_path_survives_a_pytak_without_statuswriter(self, monkeypatch):
        """Not just the factory: drive a real frame through handle_data.

        This is the failure that would take the gateway down in the field, so
        it is tested end to end rather than by inspecting make_status().
        """
        monkeypatch.setattr(classes, "_StatusWriter", None)

        emitted = []

        async def _capture(event):
            emitted.append(event)

        worker = APRSWorker.__new__(APRSWorker)
        worker.config = {}
        worker._logger = logging.getLogger("test")
        worker.status = classes.make_status("aprscot", "0.0.0")
        worker.put_queue = _capture

        asyncio.run(worker.handle_data(FRAME_WX_POSITION))

        # CoT still flows. That is the whole point of degrading rather than
        # raising: moving CoT is the job, reporting on it is not.
        assert len(emitted) == 1
        assert b"SUNSET" in emitted[0]

    def test_real_writer_used_when_available(self):
        if classes._StatusWriter is None:
            pytest.skip("installed pytak has no StatusWriter")
        assert not isinstance(classes.make_status("x", "0"), classes._NoStatus)
