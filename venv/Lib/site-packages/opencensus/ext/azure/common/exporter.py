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

import atexit
import threading
import time

from opencensus.common.schedule import Queue
from opencensus.common.schedule import QueueEvent
from opencensus.ext.azure.common import Options
from opencensus.trace import execution_context


class BaseExporter(object):
    def __init__(self, **options):
        options = Options(**options)
        self.export_interval = options.export_interval
        self.max_batch_size = options.max_batch_size
        # TODO: queue should be moved to tracer
        # too much refactor work, leave to the next PR
        self._queue = Queue(capacity=8192)  # TODO: make this configurable
        # TODO: worker should not be created in the base exporter
        self._worker = Worker(self._queue, self)
        self._worker.start()
        atexit.register(self._worker.stop, options.grace_period)

    # Ideally we don't want to have `emit`
    # Exporter will have one public method - `export`, which is a blocking
    # method, running inside worker threads.
    def emit(self, batch, event=None):
        raise NotImplementedError  # pragma: NO COVER

    # TODO: we shouldn't have this at the beginning
    # Tracer should own the queue, exporter shouldn't even know if the
    # source is a queue or not.
    # Tracer puts span_data into the queue.
    # Worker gets span_data from the src (here is the queue) and feed into
    # the dst (exporter).
    # Exporter defines the MTU (max_batch_size) and export_interval.
    # There can be one worker for each queue, or multiple workers for each
    # queue, or shared workers among queues (e.g. queue for traces, queue
    # for logs).
    def export(self, items):
        self._queue.puts(items, block=False)  # pragma: NO COVER


class Worker(threading.Thread):
    daemon = True

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self._stopping = False
        super(Worker, self).__init__()

    def run(self):  # pragma: NO COVER
        # Indicate that this thread is an exporter thread.
        execution_context.set_is_exporter(True)
        src = self.src
        dst = self.dst
        while True:
            batch = src.gets(dst.max_batch_size, dst.export_interval)
            if batch and isinstance(batch[-1], QueueEvent):
                dst.emit(batch[:-1], event=batch[-1])
                if batch[-1] is src.EXIT_EVENT:
                    break
                else:
                    continue
            dst.emit(batch)

    def stop(self, timeout=None):  # pragma: NO COVER
        start_time = time.time()
        wait_time = timeout
        if self.is_alive() and not self._stopping:
            self._stopping = True
            self.src.put(self.src.EXIT_EVENT, block=True, timeout=wait_time)
            elapsed_time = time.time() - start_time
            wait_time = timeout and max(timeout - elapsed_time, 0)
        if self.src.EXIT_EVENT.wait(timeout=wait_time):
            return time.time() - start_time  # time taken to stop
