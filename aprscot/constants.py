#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""APRSCOT Constants."""

import re

# 3833.55N/12248.93W
LL_REX = re.compile(
    r"(?P<aprs_lat>\d{4}\.\d{2})[NS][^\n]{1}(?P<aprs_lng>\d{5}\.\d{2})[EW]"
)

DEFAULT_APRSIS_PORT: int = 14580
DEFAULT_APRSIS_HOST: str = "rotate.aprs.net"
DEFAULT_APRSIS_CALLSIGN: str = "SUNSET"
DEFAULT_APRSIS_PASSCODE: str = "-1"
DEFAULT_APRSIS_FILTER: str = "m/50"

DEFAULT_COT_TYPE: str = "a-f-G-I-U-T-r"
DEFAULT_COT_STALE: str = "3600"
