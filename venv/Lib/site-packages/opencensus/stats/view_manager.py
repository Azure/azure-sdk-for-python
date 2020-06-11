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

from opencensus.common import utils
from opencensus.stats.measure_to_view_map import MeasureToViewMap
from opencensus.stats import execution_context


class ViewManager(object):
    """View Manager allows the registering of Views for collecting stats
    and receiving stats data as View Data"""
    def __init__(self):
        self.time = utils.to_iso_str()
        if execution_context.get_measure_to_view_map() == {}:
            execution_context.set_measure_to_view_map(MeasureToViewMap())

        self._measure_view_map = execution_context.get_measure_to_view_map()

    @property
    def measure_to_view_map(self):
        """the current measure to view map for the View Manager"""
        return self._measure_view_map

    def register_view(self, view):
        """registers the given view"""
        self.measure_to_view_map.register_view(view=view, timestamp=self.time)

    def get_view(self, view_name):
        """gets the view given the view name """
        return self.measure_to_view_map.get_view(view_name=view_name,
                                                 timestamp=self.time)

    def get_all_exported_views(self):
        """returns all of the exported views for the current measure to view
        map"""
        return self.measure_to_view_map.exported_views

    def register_exporter(self, exporter):
        """register the exporter"""
        self.measure_to_view_map.exporters.append(exporter)

    def unregister_exporter(self, exporter):
        """unregister the exporter"""
        self.measure_to_view_map.exporters.remove(exporter)
