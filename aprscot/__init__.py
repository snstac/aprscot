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

__version__ = "8.0.0-beta2"

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
    )

    from .functions import aprs_to_cot, create_tasks  # NOQA

    from .classes import APRSWorker  # NOQA
except ImportError as exc:
    import warnings

    warnings.warn(f"COMPAT: CI. Ignoring Exception {str(exc)}")
