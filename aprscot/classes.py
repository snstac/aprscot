#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Class Definitions."""

import logging
import socket
import threading
import time

import pycot

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


class APRSCoT(threading.Thread):

    """APRS Cursor-on-Target Threaded Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprscot.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprscot.LOG_LEVEL)
        _console_handler.setFormatter(aprscot.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprs_interface, cot_host: str) -> None:
        self.aprs_interface = aprs_interface
        self.cot_host: str = cot_host

        # Thread stuff:
        threading.Thread.__init__(self)
        self._stopped = False

    def stop(self):
        """Stops the thread at the next opportunity."""
        self._stopped = True
        return self._stopped

    def send_cot(self, aprs_frame):
        """Sends an APRS Frame to a Cursor-on-Target Host."""
        cot_event = aprscot.aprs_to_cot(aprs_frame)
        if cot_event is None:
            return False

        rendered_event = cot_event.render(encoding='UTF-8', standalone=True)

        self._logger.debug(
            'Sending CoT to %s : "%s"', self.cot_host, rendered_event)

        self.net_client.sendall(rendered_event)

    def run(self):
        """Runs this Thread, reads APRS & outputs CoT."""
        self._logger.info('Running APRSCoT Thread...')
        self.net_client = pycot.NetworkClient(self.cot_host)
        self.aprs_interface.consumer(self.send_cot)
