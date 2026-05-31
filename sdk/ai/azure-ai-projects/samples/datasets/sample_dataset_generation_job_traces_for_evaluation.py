# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from an agent's recent conversation
    traces. The sample runs in one of two modes:

      * Self-contained mode (default): Creates a temporary Foundry agent,
        runs a few sample conversations against it with GenAI content
        tracing enabled so spans flow to Application Insights, waits for
        ingestion, then runs the data generation job. The temporary agent
        and conversations are deleted at the end. Use this mode to try the
        sample without preparing anything in advance.
      * Bring-your-own-agent mode (BYO): Set FOUNDRY_AGENT_NAME to point at
        an existing agent that already has recent conversation traces. The
        sample skips agent creation and trace seeding and uses your agent
        as-is.

    In both modes, the sample:
      1. Creates a `DataGenerationJob` (scenario=EVALUATION, type=traces)
         that reads spans from Application Insights for the agent within a
         time window and synthesizes question / answer pairs into a new
         versioned Dataset.
      2. Polls the job to completion and resolves the resulting
         `DatasetVersion`.
      3. Cleans up the generated dataset, the data generation job, and
         (in self-contained mode) the temporary agent and conversations.

    The Traces source consumes existing telemetry, so no `model_options`
    are required — the service derives samples directly from the agent's
    traces.

USAGE:
    python sample_dataset_generation_job_traces_for_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv \\
        azure-monitor-opentelemetry azure-core-tracing-opentelemetry

    (The two telemetry packages are only required for self-contained mode.)

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_AGENT_NAME - Optional. The name of an existing agent (Foundry
       Agent or OpenTelemetry-instrumented third-party agent) that already
       has recent conversation traces in Application Insights. If set, the
       sample skips agent creation and trace seeding and uses this agent.
    3) FOUNDRY_MODEL_NAME - Required for self-contained mode. The Azure OpenAI
       deployment name used to drive the temporary agent during trace
       seeding. Ignored when FOUNDRY_AGENT_NAME is set.
    4) DATASET_NAME - Optional. Name to assign to the generated output
       dataset. Defaults to `traces-eval-sample`. The service caps the
       rendered output name at 50 characters, so keep custom values short —
       the sample appends a unique run id suffix.
    5) FOUNDRY_TRACES_WINDOW_DAYS - Optional. How far back, in days, to look
       for agent traces when in BYO mode. Defaults to 7. Ignored in
       self-contained mode (the sample uses an exact window covering the
       seeded traces).
    6) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between
       status polls for the data generation job. Defaults to 10.
    7) TRACE_SEEDING_CONVERSATIONS - Optional. Number of conversations to
       seed in self-contained mode. Defaults to 3.
    8) TRACE_SEEDING_TURNS - Optional. Turns per seeded conversation in
       self-contained mode. Defaults to 5.
    9) TRACE_INGESTION_WAIT_SECONDS - Optional. Seconds to wait after seeding
       for Application Insights to ingest the emitted spans before
       submitting the data generation job. Defaults to 180.
"""

import importlib
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    JobStatus,
    PromptAgentDefinition,
    TracesDataGenerationJobOptions,
    TracesDataGenerationJobSource,
)

load_dotenv()

# Persona used when seeding traces in self-contained mode. Mirrors the
# Widgets & Gizmos persona from
# sample_dataset_generation_job_simpleqna_with_agent_source.py so the
# generated traces have substantive multi-turn content the data generation
# service can synthesize useful eval samples from.
AGENT_INSTRUCTIONS = """\
You are the Widgets & Gizmos customer-support agent. Help customers with
returns, warranty claims, repairs, product specifications, compatibility,
and ordering for Widgets, Gizmos, Sprockets, and accessories.

Use this knowledge base when answering. Cite the relevant policy or spec
directly when you can.

Returns
  * Unopened products may be returned within 30 days for a full refund.
  * Opened products may be returned within 14 days for a refund minus a
    10% restocking fee. Defective products may be returned within 90 days
    at no cost.
  * Refunds are processed within 5-7 business days after the return is
    received and inspected.
  * Items lost in shipping should be reported within 21 days of the order
    date; we re-ship at no cost.

Warranty
  * Standard products carry a 1-year limited warranty against
    manufacturing defects.
  * The Deluxe Sprocket carries a 5-year limited warranty.
  * Warranty repairs are free. Customer ships the unit to us prepaid; we
    cover return shipping. Typical turnaround is 10-14 business days.

Specifications
  * Standard Widget: 4 inches, blue or red, weighs 6oz, made of aluminum.
  * Compact Widget: 2 inches, gray only, weighs 3oz, made of aluminum.
  * Gizmo: 6 inches, available in green, weighs 10oz, made of stainless
    steel and ABS plastic. Compatible with all Sprocket Adapter v2 mounts.
  * Sprocket Adapter v2: universal mount that fits Widgets, Gizmos, and
    third-party 1/4-20 hardware.

Pricing & bundles
  * Standard Widget: $19.99 each, bundle of 10 for $149.99.
  * Gizmo: $34.99 each, bundle of 5 for $129.99.
  * Deluxe Sprocket: $79.99 each.

If you do not know the answer, say so and offer to escalate. Be concise.
"""

# Multi-turn conversation arcs used to seed traces. Each inner list is one
# conversation; the sample runs each turn against the temporary agent.
SEEDING_CONVERSATION_ARCS = [
    [
        "Hi, I need to return a defective Standard Widget.",
        "I bought it 45 days ago. Is it still eligible for a refund?",
        "What about a Gizmo I ordered but never received - it has been 3 weeks?",
        "Can I get a refund instead of a replacement shipment?",
        "How long will the refund take to show up on my card?",
    ],
    [
        "Does the Deluxe Sprocket come with a warranty?",
        "What exactly does the warranty cover?",
        "My Deluxe Sprocket stopped turning after 6 months - what should I do?",
        "Do I have to pay for return shipping on a warranty claim?",
        "How long do warranty repairs usually take?",
    ],
    [
        "What is the difference between a Standard Widget and a Compact Widget?",
        "Is the Compact Widget compatible with the Sprocket Adapter v2?",
        "What colors and sizes are Gizmos available in?",
        "How much is a bundle of 10 Standard Widgets?",
        "Do you carry any third-party accessories that fit the Sprocket Adapter v2?",
    ],
]

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
provided_agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "").strip()
dataset_name = os.environ.get("DATASET_NAME", "traces-eval-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Self-contained mode is enabled unless the user pointed at an existing agent.
seed_traces = not provided_agent_name

# Window default differs by mode: in self-contained mode we compute the
# window exactly around the seeded traces (so this knob is ignored).
traces_window_days = int(os.environ.get("FOUNDRY_TRACES_WINDOW_DAYS", "7"))

# Seeding knobs (only used when seed_traces is True).
trace_seeding_conversations = int(
    os.environ.get("TRACE_SEEDING_CONVERSATIONS", str(len(SEEDING_CONVERSATION_ARCS)))
)
trace_seeding_turns = int(
    os.environ.get("TRACE_SEEDING_TURNS", str(len(SEEDING_CONVERSATION_ARCS[0])))
)
trace_ingestion_wait_seconds = int(os.environ.get("TRACE_INGESTION_WAIT_SECONDS", "180"))

if seed_traces and "FOUNDRY_MODEL_NAME" not in os.environ:
    raise EnvironmentError(
        "Self-contained mode requires FOUNDRY_MODEL_NAME (the Azure OpenAI deployment "
        "name used to drive the temporary agent). Either set FOUNDRY_MODEL_NAME or set "
        "FOUNDRY_AGENT_NAME to use an existing agent with traces."
    )

# Unique per-run output dataset name so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# Agent name used to read traces. In self-contained mode we use a unique
# per-run name so concurrent runs do not collide and so we know any matched
# traces belong to this run.
agent_name = provided_agent_name or f"traces-eval-sample-{run_id}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}


def _safe_console(text: str) -> str:
    """Encode `text` so it always prints on the active stdout encoding.

    Some Windows consoles default to cp1252, which cannot encode characters
    the model may emit (e.g. smart quotes, non-breaking hyphens). We replace
    any unencodable code points with `?` so a preview line never crashes the
    sample.
    """
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def _seed_agent_traces(
    project_client: AIProjectClient,
    agent_name_to_use: str,
    agent_id_to_use: str,
    conversation_count: int,
    turns_per_conversation: int,
    conversation_ids: List[str],
) -> None:
    """Run a few conversations against the agent so GenAI spans flow to App Insights.

    Created conversation IDs are appended to `conversation_ids` as each
    conversation is created, so the caller can clean them up even if seeding
    raises mid-way through.
    """
    arcs = SEEDING_CONVERSATION_ARCS
    with project_client.get_openai_client() as openai_client:
        for ci in range(conversation_count):
            arc = arcs[ci % len(arcs)]
            conversation = openai_client.conversations.create()
            conversation_ids.append(conversation.id)
            print(f"  - conversation {ci + 1}/{conversation_count} (id: {conversation.id})")
            for ti in range(turns_per_conversation):
                prompt = arc[ti % len(arc)]
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input=prompt,
                    extra_body={
                        "agent_reference": {
                            "name": agent_name_to_use,
                            "id": agent_id_to_use,
                            "type": "agent_reference",
                        }
                    },
                )
                preview = (response.output_text or "").replace("\n", " ")
                if len(preview) > 80:
                    preview = preview[:77] + "..."
                print(_safe_console(f"      turn {ti + 1}: {prompt}"))
                print(_safe_console(f"        response: {preview}"))


mode_label = (
    "self-contained (will create a temporary agent and seed traces)"
    if seed_traces
    else f"bring-your-own-agent (`{provided_agent_name}`)"
)
print(f"Mode: {mode_label}.")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    created_agent = None
    conversation_ids: List[str] = []
    seed_start: Optional[datetime] = None
    submitted_job_id: Optional[str] = None
    created_dataset: Optional[DatasetVersion] = None

    try:
        if seed_traces:
            # --------------------------------------------------------------
            # 0a. Wire up Azure Monitor + GenAI instrumentation so calls to
            #     responses.create emit semantic GenAI spans (with message
            #     content) to Application Insights.
            # --------------------------------------------------------------
            try:
                configure_azure_monitor = importlib.import_module(
                    "azure.monitor.opentelemetry"
                ).configure_azure_monitor
                AIProjectInstrumentor = importlib.import_module(
                    "azure.ai.projects.telemetry"
                ).AIProjectInstrumentor
            except ImportError as exc:
                raise ImportError(
                    "Self-contained mode requires the `azure-monitor-opentelemetry` and "
                    "`azure-core-tracing-opentelemetry` packages. Install them with "
                    "`pip install azure-monitor-opentelemetry azure-core-tracing-opentelemetry` "
                    "or set FOUNDRY_AGENT_NAME to use an existing agent with traces."
                ) from exc

            # AIProjectInstrumentor requires this env var be set BEFORE
            # instrument() is called. We force it on (not setdefault) so the
            # temporary agent's calls always produce GenAI spans the data-gen
            # service can read.
            os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

            print("Fetch Application Insights connection string and configure Azure Monitor exporter.")
            connection_string = project_client.telemetry.get_application_insights_connection_string()
            configure_azure_monitor(connection_string=connection_string)
            AIProjectInstrumentor().instrument(enable_content_recording=True)

            # --------------------------------------------------------------
            # 0b. Create the temporary agent.
            # --------------------------------------------------------------
            model_deployment = os.environ["FOUNDRY_MODEL_NAME"]
            print(f"Create temporary agent `{agent_name}` (model: `{model_deployment}`).")
            created_agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model_deployment,
                    instructions=AGENT_INSTRUCTIONS,
                ),
            )
            print(
                f"Agent created (id: {created_agent.id}, name: {created_agent.name}, "
                f"version: {created_agent.version})."
            )

            # --------------------------------------------------------------
            # 0c. Seed traces by running a few conversations against the agent.
            # --------------------------------------------------------------
            seed_start = datetime.now(tz=timezone.utc)
            print(
                f"Seed {trace_seeding_conversations} conversation(s) x "
                f"{trace_seeding_turns} turn(s) against the agent so spans flow to Application Insights."
            )
            _seed_agent_traces(
                project_client=project_client,
                agent_name_to_use=created_agent.name,
                agent_id_to_use=created_agent.id,
                conversation_count=trace_seeding_conversations,
                turns_per_conversation=trace_seeding_turns,
                conversation_ids=conversation_ids,
            )

            # Flush any buffered spans so the only delay we wait for below is
            # ingestion delay, not exporter batching delay.
            try:
                from opentelemetry import trace as _otel_trace  # pylint: disable=import-outside-toplevel

                tracer_provider = _otel_trace.get_tracer_provider()
                force_flush = getattr(tracer_provider, "force_flush", None)
                if callable(force_flush):
                    force_flush()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not force-flush tracer provider: {exc}")

            print(
                f"Wait {trace_ingestion_wait_seconds}s for Application Insights to ingest the "
                f"emitted spans. Override with TRACE_INGESTION_WAIT_SECONDS.",
                flush=True,
            )
            time.sleep(trace_ingestion_wait_seconds)

        # ------------------------------------------------------------------
        # 1. Submit a data generation job that reads agent traces.
        # ------------------------------------------------------------------
        if seed_traces and seed_start is not None:
            # Window covers a small backoff before seeding through "now", which
            # guarantees the seeded spans fall inside the queried window.
            start_time = seed_start - timedelta(minutes=5)
            end_time = datetime.now(tz=timezone.utc)
        else:
            # BYO mode: use the user-configurable look-back window.
            end_time = datetime.now(tz=timezone.utc)
            start_time = end_time - timedelta(days=traces_window_days)

        print(
            f"Create a data generation job from traces for agent `{agent_name}` "
            f"(window: {start_time.isoformat()} .. {end_time.isoformat()})."
        )
        job = DataGenerationJob(
            inputs=DataGenerationJobInputs(
                name=f"traces-eval-{run_id}",
                scenario=DataGenerationJobScenario.EVALUATION,
                sources=[
                    TracesDataGenerationJobSource(
                        description="Application Insights conversation traces for the Foundry agent.",
                        agent_name=agent_name,
                        start_time=start_time,
                        end_time=end_time,
                    ),
                ],
                options=TracesDataGenerationJobOptions(
                    # Service requires max_samples to be between 15 and 1000.
                    max_samples=15,
                ),
                output_options=DataGenerationJobOutputOptions(name=output_dataset_name),
            ),
        )
        job = project_client.beta.datasets.create_generation_job(job=job)
        submitted_job_id = job.id
        print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

        print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
        while True:
            job = project_client.beta.datasets.get_generation_job(job_id=job.id)
            if job.status in TERMINAL_STATUSES:
                break
            time.sleep(poll_interval_seconds)
            print(".", end="", flush=True)
        print()
        print(f"Final job status: `{job.status}`.")

        if job.status != JobStatus.SUCCEEDED:
            message = job.error.message if job.error is not None else "<no error message>"
            raise RuntimeError(f"Job `{job.id}` ended with status `{job.status}`: {message}")

        # Locate the Dataset output produced by the job.
        output_name: str = ""
        output_version: str = ""
        for output in (job.result.outputs if job.result is not None else None) or []:
            if isinstance(output, DatasetDataGenerationJobOutput):
                output_name = output.name or ""
                output_version = output.version or ""
                break
        if not output_name or not output_version:
            raise RuntimeError(f"Job `{job.id}` did not produce a dataset output.")

        dataset: DatasetVersion = project_client.datasets.get(name=output_name, version=output_version)
        created_dataset = dataset
        print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
        if job.result is not None and job.result.generated_samples is not None:
            print(f"Generated samples: {job.result.generated_samples}")

    finally:
        # Best-effort cleanup. Each step is wrapped in its own try/except so a
        # failure in one does not skip the others, and so cleanup never masks
        # the real exception that brought us here. Order is outputs -> producers:
        # dataset -> job -> seeded conversations -> temporary agent.
        if created_dataset is not None:
            try:
                print(
                    f"Delete the generated dataset `{created_dataset.name}` v{created_dataset.version}."
                )
                project_client.datasets.delete(
                    name=created_dataset.name or "", version=created_dataset.version or ""
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(
                    f"  (warning) could not delete generated dataset "
                    f"`{created_dataset.name}` v{created_dataset.version}: {exc}"
                )

        if submitted_job_id is not None:
            try:
                print(f"Delete the data generation job `{submitted_job_id}`.")
                project_client.beta.datasets.delete_generation_job(job_id=submitted_job_id)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(
                    f"  (warning) could not delete data generation job `{submitted_job_id}`: {exc}"
                )

        if conversation_ids:
            try:
                with project_client.get_openai_client() as openai_client:
                    for cid in conversation_ids:
                        try:
                            openai_client.conversations.delete(conversation_id=cid)
                            print(f"Deleted seeded conversation `{cid}`.")
                        except Exception as exc:  # pylint: disable=broad-exception-caught
                            print(f"  (warning) could not delete conversation `{cid}`: {exc}")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not open OpenAI client for conversation cleanup: {exc}")

        if created_agent is not None:
            try:
                project_client.agents.delete_version(
                    agent_name=created_agent.name, agent_version=created_agent.version
                )
                print(f"Deleted temporary agent `{created_agent.name}` v{created_agent.version}.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete temporary agent `{created_agent.name}`: {exc}")
