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

"""APRS to TAK Gateway."""

__version__ = "8.2.0"

# COMPAT: CI compat (was py 3.6)
try:
    from .constants import (  # NOQA
        DEFAULT_APRSIS_PORT,
        DEFAULT_COT_TYPE,
        DEFAULT_COT_STALE,
        DEFAULT_APRSIS_HOST,
        DEFAULT_APRSIS_CALLSIGN,
        DEFAULT_APRSIS_PASSCODE,
        DEFAULT_APRSIS_FILTER,
        DEFAULT_KISS_PORT,
        DEFAULT_SENSOR_KEEPALIVE_PERIOD,
        DEFAULT_SENSOR_LAT,
        DEFAULT_SENSOR_LON,
        DEFAULT_SENSOR_HAE,
        DEFAULT_SENSOR_ID,
        DEFAULT_SENSOR_COT_TYPE,
        DEFAULT_SENSOR_PAYLOAD_TYPE,
    )

    from .functions import aprs_to_cot, create_tasks, gen_sensor_cot  # NOQA

    from .classes import APRSWorker, KISSWorker, SensorWorker  # NOQA
except ImportError as exc:
    import warnings

    warnings.warn(f"COMPAT: CI. Ignoring Exception {str(exc)}")
