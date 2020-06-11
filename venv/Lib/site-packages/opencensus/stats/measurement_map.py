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

import logging

from opencensus.common import utils
from opencensus.tags import TagContext


logger = logging.getLogger(__name__)


class MeasurementMap(object):
    """Measurement Map is a map from Measures to measured values
    to be recorded at the same time

    :type measure_to_view_map: :class: '~opencensus.stats.measure_to_view_map.
                                        MeasureToViewMap'
    :param measure_to_view_map: the measure to view map that will store the
                                recorded stats with tags

    :type: attachments: dict
    :param attachments: the contextual information about the attachment value.

    """
    def __init__(self, measure_to_view_map, attachments=None):
        self._measurement_map = {}
        self._measure_to_view_map = measure_to_view_map
        self._attachments = attachments
        # If the user tries to record a negative value for any measurement,
        # refuse to record all measurements from this map. Recording negative
        # measurements will become an error in a later release.
        self._invalid = False

    @property
    def measurement_map(self):
        """the current measurement map"""
        return self._measurement_map

    @property
    def measure_to_view_map(self):
        """the current measure to view map for the measurement map"""
        return self._measure_to_view_map

    @property
    def attachments(self):
        """the current contextual information about the attachment value."""
        return self._attachments

    def measure_int_put(self, measure, value):
        """associates the measure of type Int with the given value"""
        if value < 0:
            # Should be an error in a later release.
            logger.warning("Cannot record negative values")
        self._measurement_map[measure] = value

    def measure_float_put(self, measure, value):
        """associates the measure of type Float with the given value"""
        if value < 0:
            # Should be an error in a later release.
            logger.warning("Cannot record negative values")
        self._measurement_map[measure] = value

    def measure_put_attachment(self, key, value):
        """Associate the contextual information of an Exemplar to this MeasureMap
            Contextual information is represented as key - value string pairs.
            If this method is called multiple times with the same key,
            only the last value will be kept.
        """
        if self._attachments is None:
            self._attachments = dict()

        if key is None or not isinstance(key, str):
            raise TypeError('attachment key should not be '
                            'empty and should be a string')
        if value is None or not isinstance(value, str):
            raise TypeError('attachment value should not be '
                            'empty and should be a string')

        self._attachments[key] = value

    def record(self, tags=None):
        """records all the measures at the same time with a tag_map.
        tag_map could either be explicitly passed to the method, or implicitly
        read from current runtime context.
        """
        if tags is None:
            tags = TagContext.get()
        if self._invalid:
            logger.warning("Measurement map has included negative value "
                           "measurements, refusing to record")
            return
        for measure, value in self.measurement_map.items():
            if value < 0:
                self._invalid = True
                logger.warning("Dropping values, value to record must be "
                               "non-negative")
                logger.info("Measure '{}' has negative value ({}), refusing "
                            "to record measurements from {}"
                            .format(measure.name, value, self))
                return

        self.measure_to_view_map.record(
                tags=tags,
                measurement_map=self.measurement_map,
                timestamp=utils.to_iso_str(),
                attachments=self.attachments
        )
