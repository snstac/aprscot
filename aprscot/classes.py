#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Class Definitions."""

import asyncio
import logging

import aprslib.parsing
import pycot
import pytak

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


class APRSWorker(pytak.MessageWorker):

    """APRS Cursor-on-Target Worker Class."""

    def __init__(self, event_queue: asyncio.Queue, cot_stale: int,
                 callsign: str, passcode: int = -1, aprs_host: str = None,
                 aprs_port: str = None, aprs_filter: str = None) -> None:
        super().__init__(event_queue, cot_stale)

        # APRS Parameters:
        self.callsign = callsign
        self.passcode = passcode
        self.aprs_filter = aprs_filter

        # Figure out APRS Host:
        aprs_host: str = aprs_host
        aprs_port: int = aprs_port or aprscot.DEFAULT_APRSIS_PORT

        if ':' in aprs_host:
            aprs_host, aprs_port = aprs_host.split(':')

        self.aprs_host = aprs_host
        self.aprs_port = aprs_port
        self._logger.info(
            "Using APRS Host: %s:%s", self.aprs_host, self.aprs_port)

    async def handle_message(self, message: bytes) -> None:
        self._logger.debug("message='%s'", message)

        # Skip control messages from APRS-IS:
        if b"# " in message[:2]:
            return

        # Some APRS Frame types are not supposed by aprslib yet:
        try:
            aprs_frame = aprslib.parsing.parse(message)
        except aprslib.exceptions.UnknownFormat as exc:
            self._logger.debug(exc)
            self._logger.debug("Ignoring aprslib.exceptions.UnknownFormat")
            return

        self._logger.debug("aprs_frame=%s", aprs_frame)

        event = aprscot.aprs_to_cot(aprs_frame)
        if event is None:
            self._logger.warning("Empty CoT Event")
            return

        await self._put_event_queue(event)

    async def run(self):
        """Runs this Thread, Reads from Pollers."""
        self._logger.info("Running APRSWorker")

        reader, writer = await asyncio.open_connection(
            self.aprs_host, int(self.aprs_port))

        _login = f"user {self.callsign} pass {self.passcode} vers aprscot v4.0.0"
        if self.aprs_filter:
            self._logger.info("Using APRS Filter: '%s'", self.aprs_filter)
            _login = f"{_login} filter {self.aprs_filter}"
        _login = f"{_login}\r\n"

        b_login = bytes(_login, 'UTF-8')
        writer.write(b_login)
        await writer.drain()

        while 1:
            frame = await reader.readline()
            if frame:
                await self.handle_message(frame)
