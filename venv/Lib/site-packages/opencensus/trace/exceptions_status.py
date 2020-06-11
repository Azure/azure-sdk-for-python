# Copyright 2017, OpenCensus Authors
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

from google.rpc import code_pb2
from opencensus.trace.status import Status

CANCELLED = Status(code_pb2.CANCELLED)
INVALID_URL = Status(code_pb2.INVALID_ARGUMENT, message='invalid URL')
TIMEOUT = Status(code_pb2.DEADLINE_EXCEEDED, message='request timed out')


def unknown(exception):
    return Status.from_exception(exception)
