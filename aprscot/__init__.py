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

"""
APRS Cursor-on-Target Gateway.
~~~~

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2022 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aprscot>
"""

from .constants import (  # NOQA
    LOG_FORMAT,
    LOG_LEVEL,
    DEFAULT_APRSIS_PORT,
    DEFAULT_COT_TYPE,
    DEFAULT_COT_STALE,
    DEFAULT_APRSIS_HOST,
    DEFAULT_APRSIS_CALLSIGN,
    DEFAULT_APRSIS_FILTER,
)

from .functions import aprs_to_cot, create_tasks  # NOQA

from .classes import APRSWorker  # NOQA

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
__source__ = "https://github.com/ampledata/aprscot"
