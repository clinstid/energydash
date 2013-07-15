#!/usr/bin/env python

################################################################################
# file:        utc_conversion.py
# description: UTC and other date/time conversion utilities
################################################################################
# Copyright 2013 Chris Linstid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from datetime import datetime, timedelta
import pytz

epoch = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)

def local_str_from_naive_utc_dt(naive_utc_dt, local_timezone):
    local_tz = pytz.timezone(local_timezone)
    local_time = pytz.utc.localize(naive_utc_dt).astimezone(local_tz)
    return local_time.strftime("%a %b %d %H:%M.%S %Z")

def seconds_to_dt(seconds):
    return (epoch + timedelta(seconds=seconds))

def dt_to_seconds(utc_dt):
    if not utc_dt.tzinfo:
        utc_dt = pytz.utc.localize(utc_dt)
    return int(round(((utc_dt - epoch).total_seconds())))
