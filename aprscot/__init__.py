#!/usr/bin/env python
# -*- coding: utf-8 -*-

# APRS Cursor-on-Target Gateway.

"""
APRS Cursor-on-Target Gateway.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2017 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprscot>

"""

from .constants import LOG_FORMAT, LOG_LEVEL, LL_REX  # NOQA

from .functions import aprs_to_cot  # NOQA

from .classes import APRSCOT  # NOQA

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2017 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'
