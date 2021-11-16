#!/usr/bin/env python
# -*- coding: utf-8 -*-

# APRS Cursor-on-Target Gateway.

"""
APRS Cursor-on-Target Gateway.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2021 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprscot>

"""

from .constants import (LOG_FORMAT, LOG_LEVEL, DEFAULT_APRSIS_PORT,  # NOQA
                        DEFAULT_COT_TYPE, DEFAULT_COT_STALE,
                        DEFAULT_APRSIS_HOST, DEFAULT_APRSIS_CALLSIGN,
                        DEFAULT_APRSIS_FILTER)

from .functions import aprs_to_cot  # NOQA

from .classes import APRSWorker  # NOQA

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
__source__ = "https://github.com/ampledata/aprscot"
