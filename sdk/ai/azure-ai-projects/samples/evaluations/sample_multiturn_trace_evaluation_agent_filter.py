# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Self-contained sample that evaluates multi-turn agent conversations by
    filtering Application Insights traces for a specific agent over a time
    window.

    Steps:
      1. Creates a transient agent.
      2. Seeds a few multi-turn conversations against the agent so the service
         emits traces into Application Insights.
      3. Creates a trace-based evaluation group with conversation-level
         evaluators.
      4. Submits an evaluation run with `agent_filter` (agent_name +
         agent_version, time window narrowed to the seeding interval).
         Retries the run if Application Insights ingestion is still in flight.
      5. Cleans up the evaluation, seeded conversations, and agent.

    Prerequisite: the project must have an Application Insights resource
    connected so the agent emits server-side traces.

    The `agent_filter` shape also supports:
      - `agent_id`: a single "name:version" string (see comment in code).
      - `filter_strategy="smart_filtering"`: biases trace selection toward more
        interesting conversations (enabled via --smart-filter).

USAGE:
    python sample_multiturn_trace_evaluation_agent_filter.py
    python sample_multiturn_trace_evaluation_agent_filter.py --smart-filter
    python sample_multiturn_trace_evaluation_agent_filter.py --max-traces 5

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The model deployment name used both to
       drive the agent during trace seeding and to power the AI-assisted
       evaluators.
"""

import argparse
import os
import time
import uuid
from datetime import datetime, timezone
from pprint import pprint
from typing import List

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, TestingCriterionAzureAIEvaluator

load_dotenv()


AGENT_INSTRUCTIONS = (
    "Widgets & Gizmos support agent. Be concise, empathetic, and resolve the "
    "customer's issue when possible. Policies you can quote:\n"
    " - Refunds: unopened 30 days; defective up to 90 days; refunds take 5-7 business days.\n"
    " - Exchanges: same window as refunds; exchanges do not include store credit.\n"
    " - Replacement parts: available for gizmos; flat $4.99 shipping for small parts.\n"
    " - You cannot place orders or process refunds directly; direct the customer to the website "
    "   or store. Always close with a confirmation that the customer's question is answered."
)
CONVERSATION_FLOWS: List[List[str]] = [
    [
        "I bought a widget last week and it stopped working.",
        "It is past the 30 day mark, can I still return it?",
        "How long will the refund take to process?",
        "Thanks, that answers my question.",
    ],
    [
        "Do you sell replacement parts for gizmos?",
        "How much does shipping cost for a small part?",
        "Got it, I will order it from the website. Thank you.",
    ],
    [
        "What is the difference between an exchange and a refund?",
        "If I exchange a defective gizmo, do I also get store credit?",
        "Understood, thanks for clarifying.",
    ],
]

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

POLL_INTERVAL_SECONDS = 5
INITIAL_INGEST_WAIT_SECONDS = 60
MAX_EVAL_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 60
# Service constraints for agent_filter trace_source:
#   - end_time - start_time must be >= 15 minutes.
#   - conversation-level queries exclude conversations whose first/last span is
#     within 5 minutes of either window edge, so we need >5 min of padding on
#     each side of the actual seeding window.
MIN_AGENT_FILTER_WINDOW_SECONDS = 16 * 60
AGENT_FILTER_EDGE_BUFFER_SECONDS = 6 * 60

TERMINAL_STATUSES = {"completed", "failed", "canceled"}


def main() -> None:  # pylint: disable=too-many-statements
    parser = argparse.ArgumentParser(description="Evaluate agent traces using agent_filter (self-contained).")
    parser.add_argument("--smart-filter", action="store_true", help="Use smart_filtering strategy")
    parser.add_argument(
        "--max-traces",
        type=int,
        default=len(CONVERSATION_FLOWS),
        help=f"Max traces to evaluate (default: {len(CONVERSATION_FLOWS)} = one per seeded conversation)",
    )
    args = parser.parse_args()

    run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    agent_name = f"mt-trace-agent-filter-{run_id}"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):

        created_agent = None
        created_conversation_ids: List[str] = []
        eval_object = None

        try:
            # 1. Create an agent that traces will be filtered to.
            print(f"Create agent `{agent_name}` (model: `{model_deployment_name}`).")
            created_agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(model=model_deployment_name, instructions=AGENT_INSTRUCTIONS),
            )
            print(f"Agent created (id: {created_agent.id}, version: {created_agent.version}).")

            # 2. Seed multi-turn conversations and capture the seeding window.
            # Pre-seed buffer must exceed the service's 5-min edge exclusion for
            # conversation-level queries.
            seed_start_unix = int(time.time()) - AGENT_FILTER_EDGE_BUFFER_SECONDS
            print(f"Seed {len(CONVERSATION_FLOWS)} multi-turn conversation(s) against the agent.")
            for flow in CONVERSATION_FLOWS:
                conversation = client.conversations.create()
                created_conversation_ids.append(conversation.id)
                print(f"  - conversation id: {conversation.id} ({len(flow)} turn(s))")
                for turn in flow:
                    client.responses.create(
                        conversation=conversation.id,
                        input=turn,
                        extra_body={"agent_reference": {"name": created_agent.name, "type": "agent_reference"}},
                    )

            print(f"Wait {INITIAL_INGEST_WAIT_SECONDS}s for Application Insights to ingest the spans.", flush=True)
            time.sleep(INITIAL_INGEST_WAIT_SECONDS)

            # 3. Create the trace-based evaluation group (conversation-level evaluators).
            data_source_config = {
                "type": "azure_ai_source",
                "scenario": "traces",
            }

            testing_criteria = [
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="customer_satisfaction",
                    evaluator_name="builtin.customer_satisfaction",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={"messages": "{{item.messages}}"},
                ),
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="task_completion",
                    evaluator_name="builtin.task_completion",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={"messages": "{{item.messages}}"},
                ),
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="conversation_coherence",
                    evaluator_name="builtin.coherence",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={"messages": "{{item.messages}}"},
                ),
            ]

            print("Create trace-based evaluation group.")
            eval_object = client.evals.create(
                name=f"Multi-turn Trace Evaluation (Agent Filter) {run_id}",
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,
            )
            print(f"Evaluation created (id: {eval_object.id}).")

            # 4. Submit eval runs with agent_filter narrowed to the seeding window.
            # Pad end_time so the last seeded span is >5 min from the upper edge
            # (conversation-level edge exclusion) and enforce the service-side
            # 15-min minimum window.
            run = None
            for attempt in range(1, MAX_EVAL_ATTEMPTS + 1):
                end_time_unix = max(
                    int(time.time()) + AGENT_FILTER_EDGE_BUFFER_SECONDS,
                    seed_start_unix + MIN_AGENT_FILTER_WINDOW_SECONDS,
                )

                trace_source = {
                    "type": "agent_filter",
                    "agent_name": created_agent.name,
                    "agent_version": str(created_agent.version),
                    "start_time": seed_start_unix,
                    "end_time": end_time_unix,
                    "max_traces": args.max_traces,
                }
                # Alternative shape: pass a single "name:version" string via `agent_id`:
                #   trace_source["agent_id"] = f"{created_agent.name}:{created_agent.version}"
                if args.smart_filter:
                    trace_source["filter_strategy"] = "smart_filtering"

                data_source = {
                    "type": "azure_ai_trace_data_source_preview",
                    "trace_source": trace_source,
                }

                print(
                    f"Create eval run (attempt {attempt}/{MAX_EVAL_ATTEMPTS}) for agent "
                    f"`{created_agent.name}` v{created_agent.version} "
                    f"(window: {seed_start_unix}..{end_time_unix}, max_traces={args.max_traces}"
                    f"{', smart_filtering' if args.smart_filter else ''})."
                )
                eval_run = client.evals.runs.create(
                    eval_id=eval_object.id,
                    name=f"multiturn-agent-filter-{run_id}-a{attempt}",
                    data_source=data_source,  # type: ignore
                    extra_body={"evaluation_level": "conversation"},
                )
                print(f"Eval run created (id: {eval_run.id}).")

                print("Poll eval run until terminal.", end="", flush=True)
                while True:
                    run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
                    if run.status in TERMINAL_STATUSES:
                        break
                    time.sleep(POLL_INTERVAL_SECONDS)
                    print(".", end="", flush=True)
                print()
                print(f"Final run status: `{run.status}`.")

                if run.status == "completed":
                    output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                    if output_items:
                        print(f"Run produced {len(output_items)} output item(s).")
                        print(f"Result counts: {run.result_counts}")
                        print(f"{'-' * 60}")
                        pprint(output_items)
                        print(f"{'-' * 60}")
                        print(f"Eval run report URL: {run.report_url}")
                        break
                    print(
                        f"Run completed but produced 0 output items "
                        f"(result counts: {run.result_counts}); traces likely not yet ingested."
                    )
                else:
                    print(f"Run did not complete (status: `{run.status}`, error: {run.error}).")

                if attempt == MAX_EVAL_ATTEMPTS:
                    raise RuntimeError(f"Eval run did not produce results after {MAX_EVAL_ATTEMPTS} attempts.")
                print(f"Wait {RETRY_WAIT_SECONDS}s and retry.", flush=True)
                time.sleep(RETRY_WAIT_SECONDS)

        finally:
            # Best-effort cleanup: eval object -> seeded conversations -> agent.
            if eval_object is not None:
                try:
                    client.evals.delete(eval_id=eval_object.id)
                    print(f"Deleted evaluation `{eval_object.id}`.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete evaluation: {exc}")

            for cid in created_conversation_ids:
                try:
                    client.conversations.delete(conversation_id=cid)
                    print(f"Deleted seeded conversation `{cid}`.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete conversation `{cid}`: {exc}")

            if created_agent is not None:
                try:
                    project_client.agents.delete_version(
                        agent_name=created_agent.name,
                        agent_version=created_agent.version,
                    )
                    print(f"Deleted agent `{created_agent.name}` v{created_agent.version}.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete agent: {exc}")


if __name__ == "__main__":
    main()
