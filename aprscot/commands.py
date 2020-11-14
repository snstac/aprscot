#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Commands."""

import argparse
import asyncio
import os
import queue
import sys
import time
import urllib

import aprslib
import pytak

import aprscot

# Python 3.6 support:
if sys.version_info[:2] >= (3, 7):
    from asyncio import get_running_loop
else:
    from asyncio import _get_running_loop as get_running_loop


__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


async def main(opts):
    loop = asyncio.get_running_loop()
    tx_queue: asyncio.Queue = asyncio.Queue()
    rx_queue: asyncio.Queue = asyncio.Queue()
    cot_url: urllib.parse.ParseResult = urllib.parse.urlparse(opts.cot_url)
    # Create our CoT Event Queue Worker
    reader, writer = await pytak.protocol_factory(cot_url)
    write_worker = pytak.EventTransmitter(tx_queue, writer)
    read_worker = pytak.EventReceiver(rx_queue, reader)

    # Create our Message Source (You need to implement this!)
    message_worker = aprscot.APRSWorker(
        tx_queue,
        opts.cot_stale,
        callsign=opts.callsign,
        passcode=opts.passcode,
        aprs_host=opts.aprs_host,
        aprs_filter=opts.aprs_filter
    )

    await tx_queue.put(aprscot.hello_event())

    done, pending = await asyncio.wait(
        set([message_worker.run(), read_worker.run(), write_worker.run()]),
        return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        print(f"Task completed: {task}")


def cli():
    """Command Line interface for APRS Cursor-on-Target Gateway."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-U', '--cot_url', help='URL to CoT Destination.',
        required=True
    )
    parser.add_argument(
        '-K', '--fts_token', help='FreeTAKServer REST API Token.'
    )
    parser.add_argument(
        '-S', '--cot_stale', help='CoT Stale period, in seconds',
    )

    parser.add_argument(
        '-c', '--callsign', help='APRS-IS Login Callsign',
        required=True
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

    if sys.version_info[:2] >= (3, 7):
        asyncio.run(main(opts), debug=bool(os.environ.get('DEBUG')))
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main(opts))
        finally:
            loop.close()


if __name__ == '__main__':
    cli()
