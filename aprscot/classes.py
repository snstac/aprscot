#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Class Definitions."""

import asyncio

import aprslib.parsing
import pytak

import aprscot

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
__source__ = "https://github.com/ampledata/aprscot"


class APRSWorker(pytak.MessageWorker):

    """APRS Cursor-on-Target Worker Class."""

    def __init__(self, event_queue: asyncio.Queue, config: dict) -> None:
        super().__init__(event_queue)
        self.config = config

        # APRS Parameters:
        self.passcode = "-1"

        self.callsign: str = config["aprscot"].get(
            "CALLSIGN", aprscot.DEFAULT_APRSIS_CALLSIGN)

        self.aprs_filter: str = config["aprscot"].get(
            "APRSIS_FILTER", aprscot.DEFAULT_APRSIS_FILTER)

        # Figure out APRS Host:
        aprs_host: str = config["aprscot"].get(
            "APRS_HOST", aprscot.DEFAULT_APRSIS_HOST)
        aprs_port: str = config["aprscot"].get(
            "APRS_PORT", aprscot.DEFAULT_APRSIS_PORT)

        if ':' in aprs_host:
            aprs_host, aprs_port = aprs_host.split(':')

        self.aprs_host = aprs_host
        self.aprs_port = aprs_port
        self._logger.info(
            "Using APRS-IS server: %s:%s", self.aprs_host, self.aprs_port)

    async def handle_message(self, message: bytes) -> None:
        """Handles messages from APRS Worker."""
        self._logger.debug("APRS message='%s'", message)

        # Skip control messages from APRS-IS:
        if b"# " in message[:2]:
            self._logger.info("APRS-IS: '%s'", message)
            return

        # Some APRS Frame types are not supported by aprslib yet:
        try:
            aprs_frame = aprslib.parsing.parse(message)
        except aprslib.exceptions.UnknownFormat as exc:
            self._logger.warning("Unhandled APRS Frame: '%s'", message)
            return
        except aprslib.exceptions.ParseError as exc2:
            self._logger.warning("Invalid Format: '%s'", message)
            return

        # self._logger.debug("aprs_frame=%s", aprs_frame)

        event = aprscot.aprs_to_cot(aprs_frame, self.config)
        if not event:
            self._logger.warning(
                "Empty CoT Event for APRS Frame: '%s'", aprs_frame.get("raw"))
            return

        await self._put_event_queue(event)

    async def run(self):  # pylint: disable=arguments-differ
        """Runs this Thread, Reads from Pollers."""
        self._logger.info("Running APRSWorker")

        reader, writer = await asyncio.open_connection(
            self.aprs_host, int(self.aprs_port))

        _login = (
            f"user {self.callsign} pass {self.passcode} vers aprscot v5.0.0")

        if self.aprs_filter:
            self._logger.info("Using APRS Filter: '%s'", self.aprs_filter)
            _login = f"{_login} filter {self.aprs_filter}"
        _login = f"{_login}\r\n"

        b_login = bytes(_login, "UTF-8")
        writer.write(b_login)
        await writer.drain()

        while 1:
            frame = await reader.readline()
            if frame:
                await self.handle_message(frame)
