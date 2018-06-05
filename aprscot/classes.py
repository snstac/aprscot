#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Class Definitions."""

import logging
import socket
import threading

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


class APRSCOT(threading.Thread):

    """APRS Cursor-on-Target Threaded Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprscot.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprscot.LOG_LEVEL)
        _console_handler.setFormatter(aprscot.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprs_interface, cot_host):
        self.aprs_interface = aprs_interface
        self.cot_host = cot_host
        threading.Thread.__init__(self)
        self._stopped = False

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._stopped = True
        return self._stopped

    def send_cot(self, aprs_frame):
        """Sends an APRS Frame to a Cursor-on-Target Host."""
        self._logger.debug('Handling frame="%s"', aprs_frame)
        cot_event = aprscot.aprs_to_cot(aprs_frame)
        if cot_event is None:
            return

        if ':' in self.cot_host:
            addr, port = self.cot_host.split(':')
        else:
            addr = self.cot_host
            port = 18999

        full_addr = (addr, int(port))
        rendered_event = bytes(cot_event.render(standalone=True), 'utf8')

        self._logger.debug('Sending to %s: "%s"', full_addr, rendered_event)

        cot_int = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cot_int.sendto(rendered_event, full_addr)

    def run(self):
        self._logger.info('Running Thread %s', self)
        self.aprs_interface.connect()
        self._logger.info('Connected to APRS-IS.')
        self.aprs_interface.consumer(self.send_cot)
