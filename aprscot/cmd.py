#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Gateway Commands."""

import argparse
import time

import aprs

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
        '-f', '--filter', help='APRS Filter', default='m/10'
    )
    opts = parser.parse_args()

    aprs_i = aprs.TCP(opts.callsign, opts.passcode, aprs_filter=opts.filter)
    aprscot_i = aprscot.APRSCOT(aprs_i, opts.cot_host)

    try:
        aprs_i.start()
        aprscot_i.start()

        while aprscot_i.is_alive():
            time.sleep(0.01)
    except KeyboardInterrupt:
        aprscot_i.stop()
    finally:
        aprscot_i.stop()


if __name__ == '__main__':
    cli()
