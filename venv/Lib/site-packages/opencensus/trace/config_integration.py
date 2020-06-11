# Copyright 2017, OpenCensus Authors
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

import importlib
import logging

log = logging.getLogger(__name__)


def trace_integrations(integrations, tracer=None):
    """Enable tracing on the selected integrations.
    :type integrations: list
    :param integrations: The integrations to be traced.
    """
    integrated = []

    for item in integrations:
        module_name = 'opencensus.ext.{}.trace'.format(item)
        try:
            module = importlib.import_module(module_name)
            module.trace_integration(tracer=tracer)
            integrated.append(item)
        except Exception as e:
            log.warning('Failed to integrate module: {}'.format(module_name))
            log.warning('{}'.format(e))

    return integrated
