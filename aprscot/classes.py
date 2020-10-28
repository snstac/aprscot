#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Class Definitions."""

import logging
import queue
import socket
import threading
import time

import aprslib
import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


class APRSWorker(threading.Thread):

    """APRS Cursor-on-Target Threaded Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprscot.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprscot.LOG_LEVEL)
        _console_handler.setFormatter(aprscot.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, msg_queue: queue.Queue, callsign: str,
                 passcode: int = -1, aprs_host: str = None,
                 aprs_port: str = None, aprs_filter: str = None,
                 stale: int = None) -> None:
        self.msg_queue: queue.Queue = msg_queue
        self.stale: int = stale
        self.callsign = callsign
        self.passcode = passcode
        self.aprs_filter = aprs_filter

        aprs_host: str = aprs_host
        aprs_port: int = aprs_port or aprscot.DEFAULT_APRSIS_PORT

        if ':' in aprs_host:
            aprs_host, aprs_port = aprs_host.split(':')

        self.aprs_host = aprs_host
        self.aprs_port = aprs_port
        self._logger.info(
            'Using APRS Host: %s:%s', self.aprs_host, self.aprs_port)

        # Thread setup:
        threading.Thread.__init__(self)
        self.daemon = True
        self._stopper = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._logger.debug('Stopping ADSBWorker')
        self._stopper.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stopper.isSet()

    def _put_queue(self, aprs_frame: dict) -> bool:
        self._logger.debug('aprs_frame=%s', aprs_frame)
        if not aprs_frame:
            self._logger.warning('Empty APRS Frame')
            return False

        cot_event = aprscot.aprs_to_cot(aprs_frame)
        if cot_event is None:
            return False

        rendered_event = cot_event.render(encoding='UTF-8', standalone=True)

        if not rendered_event:
            self._logger.warning('Empty CoT Event')
            return False

        try:
            return self.msg_queue.put(rendered_event, True, 10)
        except queue.Full as exc:
            self._logger.exception(exc)
            self._logger.warning(
                'Lost CoT Event (queue full): "%s"', rendered_event)
            return False

    def run(self):
        """Runs this Thread, Reads from Pollers."""
        self._logger.info('Running APRSWorker')

        aprs_i = aprslib.IS(
            self.callsign,
            self.passcode,
            host=self.aprs_host,
            port=int(self.aprs_port)
        )

        if self.aprs_filter:
            self._logger.info('Using APRS Filter: %s', self.aprs_filter)
            aprs_i.set_filter(self.aprs_filter)

        aprs_i.connect()
        self.msg_queue.put(aprscot.hello_event().render(encoding='UTF-8', standalone=True))
        aprs_i.consumer(self._put_queue)
