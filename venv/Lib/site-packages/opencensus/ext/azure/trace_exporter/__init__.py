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

from opencensus.common.schedule import QueueExitEvent
from opencensus.ext.azure.common import Options, utils
from opencensus.ext.azure.common.exporter import BaseExporter
from opencensus.ext.azure.common.processor import ProcessorMixin
from opencensus.ext.azure.common.protocol import (
    Data,
    Envelope,
    RemoteDependency,
    Request,
)
from opencensus.ext.azure.common.storage import LocalFileStorage
from opencensus.ext.azure.common.transport import TransportMixin
from opencensus.trace.span import SpanKind

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

logger = logging.getLogger(__name__)

__all__ = ['AzureExporter']


class AzureExporter(BaseExporter, ProcessorMixin, TransportMixin):
    """An exporter that sends traces to Microsoft Azure Monitor.

    :param options: Options for the exporter.
    """

    def __init__(self, **options):
        self.options = Options(**options)
        utils.validate_instrumentation_key(self.options.instrumentation_key)
        self.storage = LocalFileStorage(
            path=self.options.storage_path,
            max_size=self.options.storage_max_size,
            maintenance_period=self.options.storage_maintenance_period,
            retention_period=self.options.storage_retention_period,
        )
        self._telemetry_processors = []
        super(AzureExporter, self).__init__(**options)

    def span_data_to_envelope(self, sd):
        envelope = Envelope(
            iKey=self.options.instrumentation_key,
            tags=dict(utils.azure_monitor_context),
            time=sd.start_time,
        )

        envelope.tags['ai.operation.id'] = sd.context.trace_id
        if sd.parent_span_id:
            envelope.tags['ai.operation.parentId'] = '{}'.format(
                sd.parent_span_id,
            )
        if sd.span_kind == SpanKind.SERVER:
            envelope.name = 'Microsoft.ApplicationInsights.Request'
            data = Request(
                id='{}'.format(sd.span_id),
                duration=utils.timestamp_to_duration(
                    sd.start_time,
                    sd.end_time,
                ),
                responseCode=str(sd.status.code),
                success=False,  # Modify based off attributes or status
                properties={},
            )
            envelope.data = Data(baseData=data, baseType='RequestData')
            data.name = ''
            if 'http.method' in sd.attributes:
                data.name = sd.attributes['http.method']
            if 'http.route' in sd.attributes:
                data.name = data.name + ' ' + sd.attributes['http.route']
                envelope.tags['ai.operation.name'] = data.name
                data.properties['request.name'] = data.name
            elif 'http.path' in sd.attributes:
                data.properties['request.name'] = data.name + \
                    ' ' + sd.attributes['http.path']
            if 'http.url' in sd.attributes:
                data.url = sd.attributes['http.url']
                data.properties['request.url'] = sd.attributes['http.url']
            if 'http.status_code' in sd.attributes:
                status_code = sd.attributes['http.status_code']
                data.responseCode = str(status_code)
                data.success = (
                    status_code >= 200 and status_code <= 399
                )
            elif sd.status.code == 0:
                data.success = True
        else:
            envelope.name = \
                'Microsoft.ApplicationInsights.RemoteDependency'
            data = RemoteDependency(
                name=sd.name,  # TODO
                id='{}'.format(sd.span_id),
                resultCode=str(sd.status.code),
                duration=utils.timestamp_to_duration(
                    sd.start_time,
                    sd.end_time,
                ),
                success=False,  # Modify based off attributes or status
                properties={},
            )
            envelope.data = Data(
                baseData=data,
                baseType='RemoteDependencyData',
            )
            if sd.span_kind == SpanKind.CLIENT:
                data.type = sd.attributes.get('component')
                if 'http.url' in sd.attributes:
                    url = sd.attributes['http.url']
                    # TODO: error handling, probably put scheme as well
                    data.data = url
                    parse_url = urlparse(url)
                    # target matches authority (host:port)
                    data.target = parse_url.netloc
                    if 'http.method' in sd.attributes:
                        # name is METHOD/path
                        data.name = sd.attributes['http.method'] \
                            + ' ' + parse_url.path
                if 'http.status_code' in sd.attributes:
                    status_code = sd.attributes["http.status_code"]
                    data.resultCode = str(status_code)
                    data.success = 200 <= status_code < 400
                elif sd.status.code == 0:
                    data.success = True
            else:
                data.type = 'INPROC'
                data.success = True
        # TODO: links, tracestate, tags
        for key in sd.attributes:
            # This removes redundant data from ApplicationInsights
            if key.startswith('http.'):
                continue
            data.properties[key] = sd.attributes[key]
        return envelope

    def emit(self, batch, event=None):
        try:
            if batch:
                envelopes = [self.span_data_to_envelope(sd) for sd in batch]
                envelopes = self.apply_telemetry_processors(envelopes)
                result = self._transmit(envelopes)
                if result > 0:
                    self.storage.put(envelopes, result)
            if event:
                if isinstance(event, QueueExitEvent):
                    self._transmit_from_storage()  # send files before exit
                event.set()
                return
            if len(batch) < self.options.max_batch_size:
                self._transmit_from_storage()
        except Exception:
            logger.exception('Exception occurred while exporting the data.')

    def _stop(self, timeout=None):
        self.storage.close()
        return self._worker.stop(timeout)
