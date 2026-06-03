# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Self-contained sample that runs Azure AI built-in evaluators against agent
    traces resolved server-side by `agent_id`.

    Steps:
      1. Creates a transient agent.
      2. Seeds a few single-turn prompts so the service emits traces into
         Application Insights.
      3. Creates a trace-based evaluation group with single-turn evaluators.
      4. Submits an evaluation run that uses the `azure_ai_traces` data source
         with `agent_id="<name>:<version>"`; the service resolves traces
         server-side. Retries the run if Application Insights ingestion is
         still in flight.
      5. Cleans up the evaluation, seeded conversations, and agent.

    Prerequisite: the project must have an Application Insights resource
    connected so the agent emits server-side traces. No `APPINSIGHTS_RESOURCE_ID`
    or `AGENT_ID` env vars are required - everything is self-contained.

USAGE:
    python sample_evaluations_builtin_with_traces.py
    python sample_evaluations_builtin_with_traces.py --max-traces 10
    python sample_evaluations_builtin_with_traces.py --lookback-hours 2

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
    "I bought a widget last week and it stopped working - what are my options?",
    "What is the return window for unopened widgets?",
    "Can I get store credit if I exchange a defective gizmo?",
    "How much does shipping cost for a small replacement part?",
    "How long does a refund take to show up on my card?",
]

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

POLL_INTERVAL_SECONDS = 5
INITIAL_INGEST_WAIT_SECONDS = 60
MAX_EVAL_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 60

TERMINAL_STATUSES = {"completed", "failed", "canceled"}


def _build_evaluator(name: str, evaluator_name: str) -> TestingCriterionAzureAIEvaluator:
    """Standard single-turn evaluator config for the `azure_ai_traces` data source."""
    return TestingCriterionAzureAIEvaluator(
        type="azure_ai_evaluator",
        name=name,
        evaluator_name=evaluator_name,
        data_mapping={
            "query": "{{item.query}}",
            "response": "{{item.response}}",
            "tool_definitions": "{{item.tool_definitions}}",
        },
        initialization_parameters={
            "deployment_name": model_deployment_name,
        },
    )


def main() -> None:  # pylint: disable=too-many-statements
    parser = argparse.ArgumentParser(
        description="Run built-in trace evaluators against an agent's traces (self-contained)."
    )
    parser.add_argument(
        "--max-traces",
        type=int,
        default=len(SINGLE_TURN_PROMPTS),
        help=f"Max traces to evaluate (default: {len(SINGLE_TURN_PROMPTS)} = one per seeded prompt).",
    )
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=1,
        help="Hours to look back when resolving traces server-side (default: 1).",
    )
    args = parser.parse_args()

    run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    agent_name = f"builtin-traces-{run_id}"

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

            # 2. Seed single-turn prompts so the service emits traces.
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
                _build_evaluator(name="intent_resolution", evaluator_name="builtin.intent_resolution"),
                _build_evaluator(name="task_adherence", evaluator_name="builtin.task_adherence"),
            ]

            print("Create trace-based evaluation group.")
            eval_object = client.evals.create(
                name=f"Builtin Trace Evaluation {run_id}",
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,  # type: ignore
            )
            print(f"Evaluation created (id: {eval_object.id}).")

            # 4. Submit eval runs using the `azure_ai_traces` data source with
            # agent_id set to "<name>:<version>"; the service resolves matching
            # traces server-side from Application Insights.
            agent_id_for_server = f"{created_agent.name}:{created_agent.version}"
            run = None
            for attempt in range(1, MAX_EVAL_ATTEMPTS + 1):
                data_source = {
                    "type": "azure_ai_traces",
                    "agent_id": agent_id_for_server,
                    "lookback_hours": args.lookback_hours,
                    "max_traces": args.max_traces,
                }

                print(
                    f"Create eval run (attempt {attempt}/{MAX_EVAL_ATTEMPTS}) for agent_id "
                    f"`{agent_id_for_server}` (lookback_hours={args.lookback_hours}, "
                    f"max_traces={args.max_traces})."
                )
                eval_run = client.evals.runs.create(
                    eval_id=eval_object.id,
                    name=f"builtin-traces-{run_id}-a{attempt}",
                    metadata={"agent_id": agent_id_for_server},
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
