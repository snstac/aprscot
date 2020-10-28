#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Commands."""

import argparse
import queue
import time

import aprslib
import pytak

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


def cli():
    """Command Line interface for APRS Cursor-on-Target Gateway."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--callsign', help='APRS-IS Login Callsign', required=True
    )
    parser.add_argument(
        '-C', '--cot_host', help='Cursor-on-Target Host or Host:Port',
        required=True
    )
    parser.add_argument(
        '-P', '--cot_port', help='CoT Destination Port'
    )
    parser.add_argument(
        '-B', '--broadcast', help='UDP Broadcast CoT?',
        action='store_true'
    )
    parser.add_argument(
        '-S', '--stale', help='CoT Stale period, in hours',
    )
    parser.add_argument(
        '-p', '--passcode', help='APRS-IS Passcode', default='-1'
    )
    parser.add_argument(
        '-a', '--aprs_host', help='APRS-IS Host (or Host:Port).',
        default='rotate.aprs.net:14580'
    )
    parser.add_argument(
        '-f', '--aprs_filter',
        help='APRS-IS Filter, see: http://www.aprs-is.net/javAPRSFilter.aspx',
        default='m/10'
    )

    opts = parser.parse_args()

    threads: list = []
    msg_queue: queue.Queue = queue.Queue()

    aprsworker = aprscot.APRSWorker(
        msg_queue=msg_queue,
        callsign=opts.callsign,
        passcode=opts.passcode,
        aprs_host=opts.aprs_host,
        aprs_filter=opts.aprs_filter,
        stale=opts.stale
    )
    threads.append(aprsworker)

    worker_count = 2
    for wc in range(0, worker_count - 1):
        threads.append(
            pytak.CoTWorker(
                msg_queue=msg_queue,
                cot_host=opts.cot_host,
                cot_port=opts.cot_port,
                broadcast=opts.broadcast
            )
        )

    try:
        [thr.start() for thr in threads]  # NOQA pylint: disable=expression-not-assigned
        msg_queue.join()

        while all([thr.is_alive() for thr in threads]):
            time.sleep(0.01)
    except KeyboardInterrupt:
        [thr.stop() for thr in
         threads]  # NOQA pylint: disable=expression-not-assigned
    finally:
        [thr.stop() for thr in
         threads]  # NOQA pylint: disable=expression-not-assigned


if __name__ == '__main__':
    cli()
