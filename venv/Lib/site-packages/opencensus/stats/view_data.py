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


class ViewData(object):
    """View Data is the aggregated data for a particular view

    :type view:
    :param view: The view associated with this view data

    :type start_time: datetime
    :param start_time: the start time for this view data

    :type end_time: datetime
    :param end_time: the end time for this view data

    """
    def __init__(self,
                 view,
                 start_time,
                 end_time):
        self._view = view
        self._start_time = start_time
        self._end_time = end_time
        self._tag_value_aggregation_data_map = {}

    @property
    def view(self):
        """the current view in the view data"""
        return self._view

    # TODO: `start_time` and `end_time` are sometimes a `datetime` object but
    # should always be a `string`.
    @property
    def start_time(self):
        """the current start time in the view data"""
        return self._start_time

    @property
    def end_time(self):
        """the current end time in the view data"""
        return self._end_time

    @property
    def tag_value_aggregation_data_map(self):
        """the current tag value aggregation map in the view data"""
        return self._tag_value_aggregation_data_map

    def start(self):
        """sets the start time for the view data"""
        self._start_time = utils.to_iso_str()

    def end(self):
        """sets the end time for the view data"""
        self._end_time = utils.to_iso_str()

    def get_tag_values(self, tags, columns):
        """function to get the tag values from tags and columns"""
        tag_values = []
        i = 0
        while i < len(columns):
            tag_key = columns[i]
            if tag_key in tags:
                tag_values.append(tags.get(tag_key))
            else:
                tag_values.append(None)
            i += 1
        return tag_values

    def record(self, context, value, timestamp, attachments=None):
        """records the view data against context"""
        if context is None:
            tags = dict()
        else:
            tags = context.map
        tag_values = self.get_tag_values(tags=tags,
                                         columns=self.view.columns)
        tuple_vals = tuple(tag_values)
        if tuple_vals not in self.tag_value_aggregation_data_map:
            self.tag_value_aggregation_data_map[tuple_vals] = \
                self.view.new_aggregation_data()
        self.tag_value_aggregation_data_map.get(tuple_vals).\
            add_sample(value, timestamp, attachments)
