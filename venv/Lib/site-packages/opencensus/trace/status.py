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


class Status(object):
    """The Status type defines a logical error model that is suitable for
    different programming environments, including REST APIs and RPC APIs.
    It is used by gRPC.

    :type code: int
    :param code: An enum value of :class: `~google.rpc.Code`.

    :type message: str
    :param message: A developer-facing error message, should be in English.

    :type details: list
    :param details: A list of messages that carry the error details.
                    There is a common set of message types for APIs to use.
                    e.g. [
                            {
                                "@type": string,
                                field1: ...,
                                ...
                            },
                         ]
                    See: https://cloud.google.com/trace/docs/reference/v2/
                         rest/v2/Status#FIELDS.details
    """
    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message
        self.details = details

    @property
    def canonical_code(self):
        return self.code

    @property
    def description(self):
        return self.message

    @property
    def is_ok(self):
        return self.canonical_code == code_pb2.OK

    def format_status_json(self):
        """Convert a Status object to json format."""
        status_json = {}

        status_json['code'] = self.canonical_code

        if self.description is not None:
            status_json['message'] = self.description

        if self.details is not None:
            status_json['details'] = self.details

        return status_json

    @classmethod
    def from_exception(cls, exc):
        return cls(
            code=code_pb2.UNKNOWN,
            message=str(exc)
        )

    @classmethod
    def as_ok(cls):
        return cls(
            code=code_pb2.OK,
        )
