#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

class MonitorExporterPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        connection_string = self.get_from_env("APPLICATIONINSIGHTS_CONNECTION_STRING")

        # Create clients
        exporter = AzureMonitorTraceExporter.from_connection_string(
            os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
        )

        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)
        span_processor = BatchExportSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

    def run_sync(self):
        """The synchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancilliary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        for _ in range(self.args.num_traces):
            with tracer.start_as_current_span("hello"):
                print("Hello, World!")

    @staticmethod
    def add_arguments(parser):
        super(MonitorExporterPerfTest, MonitorExporterPerfTest).add_arguments(parser)
        parser.add_argument('-n', '--num-traces', nargs='?', type=int, help='Number of traces to be collected. Defaults to 10', default=10)
