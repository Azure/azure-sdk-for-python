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

from opencensus.stats.measurement_map import MeasurementMap
from opencensus.stats.measure_to_view_map import MeasureToViewMap
from opencensus.stats import execution_context


class StatsRecorder(object):
    """Stats Recorder provides methods to record stats against tags

    """
    def __init__(self):
        if execution_context.get_measure_to_view_map() == {}:
            execution_context.set_measure_to_view_map(MeasureToViewMap())

        self.measure_to_view_map = execution_context.get_measure_to_view_map()

    def new_measurement_map(self):
        """Creates a new MeasurementMap in order to record stats
        :returns a MeasurementMap for recording multiple measurements
        """
        return MeasurementMap(self.measure_to_view_map)
