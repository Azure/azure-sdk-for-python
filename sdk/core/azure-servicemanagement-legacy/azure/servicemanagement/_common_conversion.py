#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import base64
import sys

from ._common_models import (
    _unicode_type,
)


def _encode_base64(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')


def _decode_base64_to_bytes(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


def _decode_base64_to_text(data):
    decoded_bytes = _decode_base64_to_bytes(data)
    return decoded_bytes.decode('utf-8')


if sys.version_info < (3,):
    def _str(value):
        if isinstance(value, unicode):
            return value.encode('utf-8')

        return str(value)
else:
    _str = str


def _str_or_none(value):
    if value is None:
        return None

    return _str(value)


def _int_or_none(value):
    if value is None:
        return None

    return str(int(value))


def _bool_or_none(value):
    if value is None:
        return None

    if isinstance(value, bool):
        if value:
            return 'true'
        else:
            return 'false'

    return str(value)


def _lower(text):
    return text.lower()
