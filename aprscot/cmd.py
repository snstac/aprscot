#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Commands."""

import argparse
import time

import aprslib

import aprscot

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def cli():
    """Command Line interface for APRS Cursor-on-Target Gateway."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )
    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-p', '--passcode', help='passcode', required=True
    )
    parser.add_argument(
        '-C', '--cot_host', help='Cursor-on-Target Host', required=True
    )
    parser.add_argument(
        '-f', '--aprs_filter', help='APRS Filter', default='m/1000'
    )
    opts = parser.parse_args()

    aprs_i = aprslib.IS(opts.callsign, opts.passcode, port=14580)
    aprs_i.set_filter(opts.aprs_filter)
    aprscot_i = aprscot.APRSCOT(aprs_i, opts.cot_host)

    try:
        aprscot_i.start()

        while aprscot_i.is_alive():
            time.sleep(0.01)
    except KeyboardInterrupt:
        aprscot_i.stop()
    finally:
        aprscot_i.stop()


if __name__ == '__main__':
    cli()
