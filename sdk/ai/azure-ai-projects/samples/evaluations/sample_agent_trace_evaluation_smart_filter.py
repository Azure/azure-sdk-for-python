# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Self-contained sample that evaluates single-turn agent traces selected via
    `agent_filter` with `filter_strategy="smart_filtering"`.

    Steps:
      1. Creates a transient agent.
      2. Seeds a handful of single-turn prompts so the service emits traces
         into Application Insights.
      3. Creates a trace-based evaluation group with single-turn evaluators.
      4. Submits an evaluation run with `agent_filter`
         (agent_name + agent_version, smart_filtering, time window narrowed to
         the seeding interval). Retries the run if Application Insights
         ingestion is still in flight.
      5. Cleans up the evaluation, seeded conversations, and agent.

    Prerequisite: the project must have an Application Insights resource
    connected so the agent emits server-side traces.

    The `agent_filter` shape also supports passing a single "name:version"
    string via `agent_id` (see comment in code). The `--no-smart-filter` flag
    disables the smart-filtering strategy if you want to evaluate every
    matching trace.

USAGE:
    python sample_agent_trace_evaluation_smart_filter.py
    python sample_agent_trace_evaluation_smart_filter.py --no-smart-filter
    python sample_agent_trace_evaluation_smart_filter.py --max-traces 3

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
# Single-turn prompts: each prompt is seeded as its own one-turn conversation so
# the service emits one trace span per item.
SINGLE_TURN_PROMPTS: List[str] = [
    "What is the return window for unopened widgets?",
    "Do you sell replacement parts for gizmos? How much is shipping for a small part?",
    "What is the difference between an exchange and a refund?",
    "Can I get a refund for a defective gizmo I bought 60 days ago?",
    "How long does a refund take to show up on my card?",
]

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

POLL_INTERVAL_SECONDS = 5
INITIAL_INGEST_WAIT_SECONDS = 60
MAX_EVAL_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 60
# Service constraints for agent_filter trace_source:
#   - end_time - start_time must be >= 15 minutes.
#   - queries exclude traces whose first/last span is within 5 minutes of
#     either window edge, so we need >5 min of padding on each side of the
#     actual seeding window.
#   - When filter_strategy="smart_filtering" is set, max_traces must be
#     between 15 and 1000. Sample seeds fewer than 15 traces; the service
#     simply returns what exists.
MIN_AGENT_FILTER_WINDOW_SECONDS = 16 * 60
AGENT_FILTER_EDGE_BUFFER_SECONDS = 6 * 60
SMART_FILTERING_MIN_MAX_TRACES = 15

TERMINAL_STATUSES = {"completed", "failed", "canceled"}


def main() -> None:  # pylint: disable=too-many-statements
    parser = argparse.ArgumentParser(
        description="Evaluate single-turn agent traces using agent_filter + smart_filtering (self-contained)."
    )
    parser.add_argument(
        "--no-smart-filter",
        action="store_true",
        help="Disable filter_strategy='smart_filtering' (evaluate every matching trace).",
    )
    parser.add_argument(
        "--max-traces",
        type=int,
        default=len(SINGLE_TURN_PROMPTS),
        help=f"Max traces to evaluate (default: {len(SINGLE_TURN_PROMPTS)} = one per seeded prompt).",
    )
    args = parser.parse_args()
    smart_filter = not args.no_smart_filter
    effective_max_traces = args.max_traces
    if smart_filter and effective_max_traces < SMART_FILTERING_MIN_MAX_TRACES:
        print(
            f"smart_filtering requires max_traces in [{SMART_FILTERING_MIN_MAX_TRACES}, 1000]; "
            f"bumping --max-traces from {effective_max_traces} to {SMART_FILTERING_MIN_MAX_TRACES}."
        )
        effective_max_traces = SMART_FILTERING_MIN_MAX_TRACES

    run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    agent_name = f"st-trace-smart-filter-{run_id}"

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

            # 2. Seed single-turn prompts and capture the seeding window.
            # Pre-seed buffer must exceed the service's 5-min edge exclusion.
            seed_start_unix = int(time.time()) - AGENT_FILTER_EDGE_BUFFER_SECONDS
            print(f"Seed {len(SINGLE_TURN_PROMPTS)} single-turn prompt(s) against the agent.")
            for prompt in SINGLE_TURN_PROMPTS:
                conversation = client.conversations.create()
                created_conversation_ids.append(conversation.id)
                print(f"  - conversation id: {conversation.id} (prompt: {prompt!r})")
                client.responses.create(
                    conversation=conversation.id,
                    input=prompt,
                    extra_body={"agent_reference": {"name": created_agent.name, "type": "agent_reference"}},
                )

            print(f"Wait {INITIAL_INGEST_WAIT_SECONDS}s for Application Insights to ingest the spans.", flush=True)
            time.sleep(INITIAL_INGEST_WAIT_SECONDS)

            # 3. Create the trace-based evaluation group (single-turn evaluators).
            data_source_config = {
                "type": "azure_ai_source",
                "scenario": "traces",
            }

            testing_criteria = [
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="task_completion",
                    evaluator_name="builtin.task_completion",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={
                        "query": "{{item.query}}",
                        "response": "{{item.response}}",
                    },
                ),
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="coherence",
                    evaluator_name="builtin.coherence",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={
                        "query": "{{item.query}}",
                        "response": "{{item.response}}",
                    },
                ),
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="violence",
                    evaluator_name="builtin.violence",
                    initialization_parameters={"model": model_deployment_name},
                    data_mapping={
                        "query": "{{item.query}}",
                        "response": "{{item.response}}",
                    },
                ),
            ]

            print("Create trace-based evaluation group.")
            eval_object = client.evals.create(
                name=f"Trace Evaluation (Agent Smart Filter) {run_id}",
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,
            )
            print(f"Evaluation created (id: {eval_object.id}).")

            # 4. Submit eval runs with agent_filter narrowed to the seeding window.
            # Pad end_time so the last seeded span is >5 min from the upper edge
            # and enforce the service-side 15-min minimum window.
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
                    "max_traces": effective_max_traces,
                }
                # Alternative shape: pass a single "name:version" string via `agent_id`:
                #   trace_source["agent_id"] = f"{created_agent.name}:{created_agent.version}"
                if smart_filter:
                    trace_source["filter_strategy"] = "smart_filtering"

                data_source = {
                    "type": "azure_ai_trace_data_source_preview",
                    "trace_source": trace_source,
                }

                print(
                    f"Create eval run (attempt {attempt}/{MAX_EVAL_ATTEMPTS}) for agent "
                    f"`{created_agent.name}` v{created_agent.version} "
                    f"(window: {seed_start_unix}..{end_time_unix}, max_traces={effective_max_traces}"
                    f"{', smart_filtering' if smart_filter else ''})."
                )
                eval_run = client.evals.runs.create(
                    eval_id=eval_object.id,
                    name=f"agent-smart-filter-{run_id}-a{attempt}",
                    data_source=data_source,  # type: ignore
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
