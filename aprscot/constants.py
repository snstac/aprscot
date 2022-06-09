#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""APRSCOT Constants."""

import logging
import os
import re

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


if bool(os.environ.get("DEBUG")):
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = logging.Formatter(
        (
            "%(asctime)s aprscot %(levelname)s %(name)s.%(funcName)s:%(lineno)d "
            " - %(message)s"
        )
    )
    logging.debug("aprscot Debugging Enabled via DEBUG Environment Variable.")
else:
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = logging.Formatter(("%(asctime)s aprscot - %(message)s"))

# 3833.55N/12248.93W
LL_REX = re.compile(
    r"(?P<aprs_lat>\d{4}\.\d{2})[NS][^\n]{1}(?P<aprs_lng>\d{5}\.\d{2})[EW]"
)

DEFAULT_APRSIS_PORT: int = 14580
DEFAULT_APRSIS_HOST: str = "rotate.aprs.net"
DEFAULT_APRSIS_CALLSIGN: str = "SUNSET"
DEFAULT_APRSIS_FILTER: str = "m/50"

DEFAULT_COT_TYPE: str = "a-f-G-I-U-T-r"
DEFAULT_COT_STALE: str = "3600"
