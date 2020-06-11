# Copyright 2018, OpenCensus Authors
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

"""Module containing base class for transport."""


class Transport(object):
    """Base class for transport.

    Subclasses of :class:`Transport` must override :meth:`export`.
    """
    def export(self, datas):
        """Export the data."""
        raise NotImplementedError

    def flush(self):
        """Submit any pending data.

        For blocking/sync transports, this is a no-op.
        """
