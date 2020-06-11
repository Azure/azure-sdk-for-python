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

from collections import defaultdict
import copy
import logging

from opencensus.stats import metric_utils
from opencensus.stats import view_data as view_data_module


class MeasureToViewMap(object):
    """Measure To View Map stores a map from names of Measures to
    specific View Datas

    """

    def __init__(self):
        # stores the one-to-many mapping from Measures to View Datas
        self._measure_to_view_data_list_map = defaultdict(list)
        # stores a map from the registered View names to the Views
        self._registered_views = {}
        # stores a map from the registered Measure names to the Measures
        self._registered_measures = {}
        # stores the set of the exported views
        self._exported_views = set()
        # Stores the registered exporters
        self._exporters = []

    @property
    def exported_views(self):
        """the current exported views"""
        return self._exported_views

    @property
    def exporters(self):
        """registered exporters"""
        return self._exporters

    def get_view(self, view_name, timestamp):
        """get the View Data from the given View name"""
        view = self._registered_views.get(view_name)
        if view is None:
            return None

        view_data_list = self._measure_to_view_data_list_map.get(
            view.measure.name)

        if not view_data_list:
            return None

        for view_data in view_data_list:
            if view_data.view.name == view_name:
                break
        else:
            return None

        return self.copy_and_finalize_view_data(view_data)

    def filter_exported_views(self, all_views):
        """returns the subset of the given view that should be exported"""
        views = set(all_views)
        return views

    # TODO: deprecate
    def register_view(self, view, timestamp):
        """registers the view's measure name to View Datas given a view"""
        if len(self.exporters) > 0:
            try:
                for e in self.exporters:
                    e.on_register_view(view)
            except AttributeError:
                pass

        self._exported_views = None
        existing_view = self._registered_views.get(view.name)
        if existing_view is not None:
            if existing_view == view:
                # ignore the views that are already registered
                return
            else:
                logging.warning(
                    "A different view with the same name is already registered"
                )  # pragma: NO COVER
        measure = view.measure
        registered_measure = self._registered_measures.get(measure.name)
        if registered_measure is not None and registered_measure != measure:
            logging.warning(
                "A different measure with the same name is already registered")
        self._registered_views[view.name] = view
        if registered_measure is None:
            self._registered_measures[measure.name] = measure
        self._measure_to_view_data_list_map[view.measure.name].append(
            view_data_module.ViewData(view=view, start_time=timestamp,
                                      end_time=timestamp))

    def record(self, tags, measurement_map, timestamp, attachments=None):
        """records stats with a set of tags"""
        assert all(vv >= 0 for vv in measurement_map.values())
        for measure, value in measurement_map.items():
            if measure != self._registered_measures.get(measure.name):
                return
            view_datas = []
            for measure_name, view_data_list \
                    in self._measure_to_view_data_list_map.items():
                if measure_name == measure.name:
                    view_datas.extend(view_data_list)
            for view_data in view_datas:
                view_data.record(
                    context=tags, value=value, timestamp=timestamp,
                    attachments=attachments)
            self.export(view_datas)

    # TODO: deprecate
    def export(self, view_datas):
        """export view datas to registered exporters"""
        view_datas_copy = \
            [self.copy_and_finalize_view_data(vd) for vd in view_datas]
        if len(self.exporters) > 0:
            for e in self.exporters:
                try:
                    e.export(view_datas_copy)
                except AttributeError:
                    pass

    def get_metrics(self, timestamp):
        """Get a Metric for each registered view.

        Convert each registered view's associated `ViewData` into a `Metric` to
        be exported.

        :type timestamp: :class: `datetime.datetime`
        :param timestamp: The timestamp to use for metric conversions, usually
        the current time.

        :rtype: Iterator[:class: `opencensus.metrics.export.metric.Metric`]
        """
        for vdl in self._measure_to_view_data_list_map.values():
            for vd in vdl:
                metric = metric_utils.view_data_to_metric(vd, timestamp)
                if metric is not None:
                    yield metric

    # TODO(issue #470): remove this method once we export immutable stats.
    def copy_and_finalize_view_data(self, view_data):
        view_data_copy = copy.copy(view_data)
        tvdam_copy = copy.deepcopy(view_data.tag_value_aggregation_data_map)
        view_data_copy._tag_value_aggregation_data_map = tvdam_copy
        view_data_copy.end()
        return view_data_copy
