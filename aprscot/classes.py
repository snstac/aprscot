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

from typing import Optional

import aprslib.parsing

import pytak
import aprscot


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
