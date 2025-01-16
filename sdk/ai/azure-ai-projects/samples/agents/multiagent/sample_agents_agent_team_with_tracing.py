# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to multiple agents using AgentTeam with traces.

USAGE:
    python sample_agents_agent_team.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""

import os, sys
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from agent_team_with_traces import AgentTeam

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

# Enable console tracing without enabling agent traces
# or, if you have local OTLP endpoint running, change it to
# exporter = ConsoleSpanExporter()
# trace.set_tracer_provider(TracerProvider())
# tracer = trace.get_tracer(__name__)
# trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

# Enable console tracing with agent traces
#project_client.telemetry.enable(destination=sys.stdout)

with project_client:
    agent_team = AgentTeam("test_team", project_client=project_client)
    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="Coder",
        instructions="You are software engineer who writes great code. Your name is Coder.",
    )
    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="Reviewer",
        instructions="You are software engineer who reviews code. Your name is Reviewer.",
    )
    agent_team.assemble_team()

    print("A team of agents specialized in software engineering is available for requests.")
    while True:
        user_input = input("Input (type 'quit' to exit): ")
        if user_input.lower() == "quit":
            break
        agent_team.process_request(request=user_input)

    agent_team.dismantle_team()
