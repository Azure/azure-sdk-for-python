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

from opencensus.common.runtime_context import RuntimeContext

_measure_to_view_map_slot = RuntimeContext.register_slot(
    'measure_to_view_map',
    lambda: {})


def get_measure_to_view_map():
    return RuntimeContext.measure_to_view_map


def set_measure_to_view_map(measure_to_view_map):
    RuntimeContext.measure_to_view_map = measure_to_view_map


def clear():
    """Clear the context, used in test."""
    _measure_to_view_map_slot.clear()
