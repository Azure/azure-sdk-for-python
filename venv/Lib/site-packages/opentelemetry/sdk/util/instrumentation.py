# Copyright The OpenTelemetry Authors
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


class InstrumentationInfo:
    """Immutable information about an instrumentation library module.

    See `opentelemetry.trace.TracerProvider.get_tracer` or
    `opentelemetry.metrics.MeterProvider.get_meter` for the meaning of these
    properties.
    """

    __slots__ = ("_name", "_version")

    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, self._name, self._version
        )

    def __hash__(self):
        return hash((self._name, self._version))

    def __eq__(self, value):
        return type(value) is type(self) and (self._name, self._version) == (
            value._name,
            value._version,
        )

    def __lt__(self, value):
        if type(value) is not type(self):
            return NotImplemented
        return (self._name, self._version) < (value._name, value._version)

    @property
    def version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return self._name
