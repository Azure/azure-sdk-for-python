# Copyright 2019, OpenCensus Authors
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

logger = logging.getLogger(__name__)


class ProcessorMixin(object):
    """ProcessorMixin adds the ability to process telemetry processors

    Telemetry processors are functions that are called before exporting of
    telemetry to possibly modify the envelope contents.
    """

    def add_telemetry_processor(self, processor):
        """Adds telemetry processor to the collection. Telemetry processors
        will be called one by one before telemetry item is pushed for sending
        and in the order they were added.

        :param processor: The processor to add.
        """
        self._telemetry_processors.append(processor)

    def clear_telemetry_processors(self):
        """Removes all telemetry processors"""
        self._telemetry_processors = []

    def apply_telemetry_processors(self, envelopes):
        """Applies all telemetry processors in the order they were added.

        This function will return the list of envelopes to be exported after
        each processor has been run sequentially. Individual processors can
        throw exceptions and fail, but the applying of all telemetry processors
        will proceed (not fast fail). Processors also return True if envelope
        should be included for exporting, False otherwise.

        :param envelopes: The envelopes to apply each processor to.
        """
        filtered_envelopes = []
        for envelope in envelopes:
            accepted = True
            for processor in self._telemetry_processors:
                try:
                    if processor(envelope) is False:
                        accepted = False
                        break
                except Exception as ex:
                    logger.warning('Telemetry processor failed with: %s.', ex)
            if accepted:
                filtered_envelopes.append(envelope)
        return filtered_envelopes
