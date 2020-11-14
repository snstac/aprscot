#!/usr/bin/env python
# -*- coding: utf-8 -*-

# APRS Cursor-on-Target Gateway.

"""
APRS Cursor-on-Target Gateway.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2020 Orion Labs, Inc.
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprscot>

"""

from .constants import (LOG_FORMAT, LOG_LEVEL, DEFAULT_APRSIS_PORT,  # NOQA
                        DEFAULT_EVENT_TYPE, DEFAULT_EVENT_STALE)

from .functions import aprs_to_cot, hello_event  # NOQA

from .classes import APRSWorker  # NOQA

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'
__source__ = 'https://github.com/ampledata/aprscot'
