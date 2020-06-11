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
import random
import threading
import time
import traceback

from opencensus.common.schedule import Queue, QueueEvent, QueueExitEvent
from opencensus.ext.azure.common import Options, utils
from opencensus.ext.azure.common.processor import ProcessorMixin
from opencensus.ext.azure.common.protocol import (
    Data,
    Envelope,
    ExceptionData,
    Message,
)
from opencensus.ext.azure.common.storage import LocalFileStorage
from opencensus.ext.azure.common.transport import TransportMixin
from opencensus.trace import execution_context

logger = logging.getLogger(__name__)

__all__ = ['AzureLogHandler']


class BaseLogHandler(logging.Handler):
    def __init__(self):
        super(BaseLogHandler, self).__init__()
        self._queue = Queue(capacity=8192)  # TODO: make this configurable
        self._worker = Worker(self._queue, self)
        self._worker.start()

    def close(self):
        self._worker.stop()

    def createLock(self):
        self.lock = None

    def emit(self, record):
        self._queue.put(record, block=False)

    def _export(self, batch, event=None):
        try:
            return self.export(batch)
        finally:
            if event:
                event.set()

    def export(self, batch):
        raise NotImplementedError  # pragma: NO COVER

    def flush(self, timeout=None):
        self._queue.flush(timeout=timeout)


class Worker(threading.Thread):
    daemon = True

    def __init__(self, src, dst):
        self._src = src
        self._dst = dst
        self._stopping = False
        super(Worker, self).__init__(
            name='{} Worker'.format(type(dst).__name__)
        )

    def run(self):
        # Indicate that this thread is an exporter thread.
        execution_context.set_is_exporter(True)
        src = self._src
        dst = self._dst
        while True:
            batch = src.gets(dst.max_batch_size, dst.export_interval)
            if batch and isinstance(batch[-1], QueueEvent):
                try:
                    dst._export(batch[:-1], event=batch[-1])
                except Exception:
                    logger.exception('Unhandled exception from exporter.')
                if batch[-1] is src.EXIT_EVENT:
                    break
                continue  # pragma: NO COVER
            try:
                dst._export(batch)
            except Exception:
                logger.exception('Unhandled exception from exporter.')

    def stop(self, timeout=None):  # pragma: NO COVER
        start_time = time.time()
        wait_time = timeout
        if self.is_alive() and not self._stopping:
            self._stopping = True
            self._src.put(self._src.EXIT_EVENT, block=True, timeout=wait_time)
            elapsed_time = time.time() - start_time
            wait_time = timeout and max(timeout - elapsed_time, 0)
        if self._src.EXIT_EVENT.wait(timeout=wait_time):
            return time.time() - start_time  # time taken to stop


class SamplingFilter(logging.Filter):

    def __init__(self, probability=1.0):
        super(SamplingFilter, self).__init__()
        self.probability = probability

    def filter(self, record):
        return random.random() < self.probability


class AzureLogHandler(TransportMixin, ProcessorMixin, BaseLogHandler):
    """Handler for logging to Microsoft Azure Monitor.

    :param options: Options for the log handler.
    """

    def __init__(self, **options):
        self.options = Options(**options)
        utils.validate_instrumentation_key(self.options.instrumentation_key)
        if not 0 <= self.options.logging_sampling_rate <= 1:
            raise ValueError('Sampling must be in the range: [0,1]')
        self.export_interval = self.options.export_interval
        self.max_batch_size = self.options.max_batch_size
        self.storage = LocalFileStorage(
            path=self.options.storage_path,
            max_size=self.options.storage_max_size,
            maintenance_period=self.options.storage_maintenance_period,
            retention_period=self.options.storage_retention_period,
        )
        self._telemetry_processors = []
        super(AzureLogHandler, self).__init__()
        self.addFilter(SamplingFilter(self.options.logging_sampling_rate))

    def close(self):
        self.storage.close()
        super(AzureLogHandler, self).close()

    def _export(self, batch, event=None):  # pragma: NO COVER
        try:
            if batch:
                envelopes = [self.log_record_to_envelope(x) for x in batch]
                envelopes = self.apply_telemetry_processors(envelopes)
                result = self._transmit(envelopes)
                if result > 0:
                    self.storage.put(envelopes, result)
            if event:
                if isinstance(event, QueueExitEvent):
                    self._transmit_from_storage()  # send files before exit
                return
            if len(batch) < self.options.max_batch_size:
                self._transmit_from_storage()
        finally:
            if event:
                event.set()

    def log_record_to_envelope(self, record):
        envelope = Envelope(
            iKey=self.options.instrumentation_key,
            tags=dict(utils.azure_monitor_context),
            time=utils.timestamp_to_iso_str(record.created),
        )

        envelope.tags['ai.operation.id'] = getattr(
            record,
            'traceId',
            '00000000000000000000000000000000',
        )
        envelope.tags['ai.operation.parentId'] = '|{}.{}.'.format(
            envelope.tags['ai.operation.id'],
            getattr(record, 'spanId', '0000000000000000'),
        )
        properties = {
            'process': record.processName,
            'module': record.module,
            'fileName': record.pathname,
            'lineNumber': record.lineno,
            'level': record.levelname,
        }

        if (hasattr(record, 'custom_dimensions') and
                isinstance(record.custom_dimensions, dict)):
            properties.update(record.custom_dimensions)

        if record.exc_info:
            exctype, _value, tb = record.exc_info
            callstack = []
            level = 0
            for fileName, line, method, _text in traceback.extract_tb(tb):
                callstack.append({
                    'level': level,
                    'method': method,
                    'fileName': fileName,
                    'line': line,
                })
                level += 1
            callstack.reverse()

            envelope.name = 'Microsoft.ApplicationInsights.Exception'
            data = ExceptionData(
                exceptions=[{
                    'id': 1,
                    'outerId': 0,
                    'typeName': exctype.__name__,
                    'message': self.format(record),
                    'hasFullStack': True,
                    'parsedStack': callstack,
                }],
                severityLevel=max(0, record.levelno - 1) // 10,
                properties=properties,
            )
            envelope.data = Data(baseData=data, baseType='ExceptionData')
        else:
            envelope.name = 'Microsoft.ApplicationInsights.Message'
            data = Message(
                message=self.format(record),
                severityLevel=max(0, record.levelno - 1) // 10,
                properties=properties,
            )
            envelope.data = Data(baseData=data, baseType='MessageData')
        return envelope
