#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Cursor-on-Target Constants."""

import logging
import os
import re

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'


if bool(os.environ.get('DEBUG')):
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = logging.Formatter(
    ('%(asctime)s aprscot %(levelname)s %(name)s.%(funcName)s:%(lineno)d '
     ' - %(message)s'))

# 3833.55N/12248.93W
LL_REX = re.compile(
    r"(?P<aprs_lat>\d{4}\.\d{2})[NS][^\n]{1}(?P<aprs_lng>\d{5}\.\d{2})[EW]"
)

DEFAULT_COT_PORT: int = 4242
DEFAULT_APRSIS_PORT: int = 14580
