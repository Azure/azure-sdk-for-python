# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys
from typing import cast
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.projects import AIProjectClient
from azure.monitor.opentelemetry import configure_azure_monitor


class AgentTraceConfigurator:
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    def enable_azure_monitor_tracing(self):
        application_insights_connection_string = self.project_client.telemetry.get_connection_string()
        if not application_insights_connection_string:
            print("Application Insights was not enabled for this project.")
            print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
            exit()
        configure_azure_monitor(connection_string=application_insights_connection_string)
        self.project_client.telemetry.enable()

    def enable_console_tracing_without_genai(self):
        exporter = ConsoleSpanExporter()
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        provider = cast(TracerProvider, trace.get_tracer_provider())
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        print("Console tracing enabled without agent traces.")

    def enable_console_tracing_with_agent(self):
        self.project_client.telemetry.enable(destination=sys.stdout)
        print("Console tracing enabled with agent traces.")

    def display_menu(self):
        print("Select a tracing option:")
        print("1. Enable Azure Monitor tracing")
        print("2. Enable console tracing without enabling gen_ai agent traces")
        print("3. Enable console tracing with gen_ai agent traces")
        print("4. Do not enable traces")

    def setup_tracing(self):
        self.display_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            self.enable_azure_monitor_tracing()
        elif choice == "2":
            self.enable_console_tracing_without_genai()
        elif choice == "3":
            self.enable_console_tracing_with_agent()
        elif choice == "4":
            print("No tracing enabled.")
        else:
            print("Invalid choice. Please select a valid option.")
