#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

import os
import uuid
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanContext
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

class MonitorExporterPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        connection_string = self.get_from_env("APPLICATIONINSIGHTS_CONNECTION_STRING")

        # Create clients
        self.exporter = AzureMonitorTraceExporter.from_connection_string(
            os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
        )

        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        self.spans_list = []
        for _ in range(self.args.num_spans):
            self.spans_list.append(trace._Span(
                name=str(uuid.uuid4()),
                context=SpanContext(
                    trace_id=uuid.uuid4(),
                    span_id=12030755672171557338,
                    is_remote=False,
                )))

    def run_sync(self):
        """The synchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancilliary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        self.exporter.export(self.spans_list)

    @staticmethod
    def add_arguments(parser):
        super(MonitorExporterPerfTest, MonitorExporterPerfTest).add_arguments(parser)
        parser.add_argument('-n', '--num-spans', nargs='?', type=int, help='Number of spans to be exported. Defaults to 10', default=10)
