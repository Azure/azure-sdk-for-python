# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helpers for general Python functionality."""

import functools

import six


# functools.partial objects lack several attributes present on real function
# objects. In Python 2 wraps fails on this so use a restricted set instead.
_PARTIAL_VALID_ASSIGNMENTS = ("__doc__",)


def wraps(wrapped):
    """A functools.wraps helper that handles partial objects on Python 2."""
    # https://github.com/google/pytype/issues/322
    if isinstance(wrapped, functools.partial):  # pytype: disable=wrong-arg-types
        return six.wraps(wrapped, assigned=_PARTIAL_VALID_ASSIGNMENTS)
    else:
        return six.wraps(wrapped)
