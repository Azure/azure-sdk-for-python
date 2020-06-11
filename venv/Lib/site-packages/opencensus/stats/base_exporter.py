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

"""Module containing base class for exporters."""


class StatsExporter(object):
    """Base class for opencensus stats exporters.

    Subclasses of :class:`Exporter` must override :meth:`export`.
    """

    def on_register_view(self, view):
        """
        :type view: object of :class:
            `~opencensus.stats.view.View`
        :param object of opencensus.stats.view.View view:
            View object to register
        """
        raise NotImplementedError  # pragma: NO COVER

    def emit(self, view_datas):
        """Send view and measurement to exporter record method,
        and then it will record on its own way.

        :type view_datas: object of :class:
            `~opencensus.stats.view_data.ViewData`
        :param list of opencensus.stats.view_data.ViewData ViewData:
            list of ViewData object to send to Stackdriver Monitoring
        """
        raise NotImplementedError  # pragma: NO COVER
