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

import itertools
import logging

from opencensus.common import utils
from opencensus.common.schedule import PeriodicTask
from opencensus.trace import execution_context


logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = 60
GRACE_PERIOD = 5


class TransportError(Exception):
    pass


class PeriodicMetricTask(PeriodicTask):
    """Thread that periodically calls a given function.

    :type interval: int or float
    :param interval: Seconds between calls to the function.

    :type function: function
    :param function: The function to call.

    :type args: list
    :param args: The args passed in while calling `function`.

    :type kwargs: dict
    :param args: The kwargs passed in while calling `function`.
    """

    daemon = True

    def __init__(self, interval=None, function=None, args=None, kwargs=None):
        if interval is None:
            interval = DEFAULT_INTERVAL

        self.func = function

        def func(*aa, **kw):
            try:
                return self.func(*aa, **kw)
            except TransportError as ex:
                logger.exception(ex)
                self.cancel()
            except Exception:
                logger.exception("Error handling metric export")

        super(PeriodicMetricTask, self).__init__(interval, func, args, kwargs)

    def run(self):
        # Indicate that this thread is an exporter thread.
        execution_context.set_is_exporter(True)
        super(PeriodicMetricTask, self).run()


def get_exporter_thread(metric_producers, exporter, interval=None):
    """Get a running task that periodically exports metrics.

    Get a `PeriodicTask` that periodically calls:

        export(itertools.chain(*all_gets))

    where all_gets is the concatenation of all metrics produced by the metric
    producers in metric_producers, each calling metric_producer.get_metrics()

    :type metric_producers:
    list(:class:`opencensus.metrics.export.metric_producer.MetricProducer`)
    :param metric_producers: The list of metric producers to use to get metrics

    :type exporter: :class:`opencensus.stats.base_exporter.MetricsExporter`
    :param exporter: The exporter to use to export metrics.

    :type interval: int or float
    :param interval: Seconds between export calls.

    :rtype: :class:`PeriodicTask`
    :return: A running thread responsible calling the exporter.

    """
    weak_gets = [utils.get_weakref(producer.get_metrics)
                 for producer in metric_producers]
    weak_export = utils.get_weakref(exporter.export_metrics)

    def export_all():
        all_gets = []
        for weak_get in weak_gets:
            get = weak_get()
            if get is None:
                raise TransportError("Metric producer is not available")
            all_gets.append(get())
        export = weak_export()
        if export is None:
            raise TransportError("Metric exporter is not available")

        export(itertools.chain(*all_gets))

    tt = PeriodicMetricTask(interval, export_all)
    tt.start()
    return tt
