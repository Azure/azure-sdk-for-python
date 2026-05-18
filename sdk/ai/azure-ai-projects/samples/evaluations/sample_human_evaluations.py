# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to emit human evaluation events from your
    application as OpenTelemetry custom events that land in the `customEvents`
    Application Insights table connected to your Microsoft Foundry project.

    Human evaluations capture signals that automated evaluators struggle with --
    tone, user satisfaction, factual nuance -- typically as a thumbs up/down
    (binary) or a 5-point rating (likert_5) provided by an end user of your
    application.

    The sample defines a small `emit_human_evaluation_event(...)` helper that
    assembles and emits OTel-compliant events that carry additional metadata
    for compatibility with Microsoft Azure services. The event is emitted via 
    Python `logging`, which `azure.monitor.opentelemetry.configure_azure_monitor` 
    routes through OpenTelemetry to Application Insights.

    NOTE: Human evaluations is in preview, and carries the risk of breaking changes.

USAGE:
    python sample_human_evaluations.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project. It has
       the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
"""

import json
import logging
import os
import uuid
from typing import Literal, Mapping, Optional

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.projects import AIProjectClient

load_dotenv()

# `configure_azure_monitor` installs an OpenTelemetry LoggingHandler on the
# root logger, so any standard Python `logging` call below this point flows
# through OTel to Application Insights as a log record. The
# `microsoft.custom_event.name` attribute is what routes the record to the
# `customEvents` table.
logger = logging.getLogger("human_evaluations")
logger.setLevel(logging.INFO)


_KIND_DEFAULTS = {
    "binary": {
        "min_value": 0.0,
        "max_value": 1.0,
        "threshold": 1.0,
        "desirable_direction": "increase",
        "type": "boolean",
    },
    "likert_5": {
        "min_value": 1.0,
        "max_value": 5.0,
        "threshold": 3.0,
        "desirable_direction": "increase",
        "type": "ordinal",
    },
}


# When identifying the end user, populate either or both of:
#   enduser_id        → the signed-in user's identity (e.g., AAD object id,
#                       email). This is PII and lands in App Insights as
#                       `user_AuthenticatedId`.
#   enduser_pseudo_id → a random, non-identifying id you generated (e.g., a
#                       browser cookie or device id). Use when the user is
#                       anonymous or you don't want to log PII. Lands in
#                       App Insights as `user_Id`.
# Signed-in users often have both: `enduser_id` says who they are, and
# `enduser_pseudo_id` lets you correlate them with their earlier anonymous
# activity from the same browser/device.
def emit_human_evaluation_event(
    *,
    evaluation_name: str,
    score_value: float,
    kind: Literal["binary", "likert_5"],
    explanation: Optional[str] = None,
    response_id: Optional[str] = None,
    project_resource_id: Optional[str] = None,
    enduser_id: Optional[str] = None,
    enduser_pseudo_id: Optional[str] = None,
    tags: Optional[Mapping[str, str]] = None,
    evaluation_id: Optional[str] = None,
) -> None:
    """Emit a single `gen_ai.evaluation.result` human evaluation event.

    The helper takes care of all the bookkeeping (deriving min/max/
    threshold/type from `kind`, deriving the pass/fail label from the score,
    JSON-encoding `internal_properties`, generating a correlation id, etc.).

    Args:
        evaluation_name: The metric being evaluated. Free-form, but pick a
            consistent snake_case name per metric.
            Examples: "task_completion", "relevance", "helpfulness".
        score_value: The numeric score the user gave. Must be a whole number
            (no fractional part), expressed as a float.
            For kind="binary": 0.0 (thumbs down) or 1.0 (thumbs up).
            For kind="likert_5": 1.0, 2.0, 3.0, 4.0, or 5.0.
        kind: The evaluation shape. "binary" for thumbs up/down; "likert_5"
            for a 1-5 star rating.
        explanation: Optional free-form text the user provided to justify
            their score.
            Example: "The agent answered the question accurately."
        response_id: Optional id of the agent response being evaluated.
            Typically the id of an OpenAI Responses API response. Used to
            correlate the evaluation back to the response it judged.
            Example: "resp_64904952b20872620069f8d600779c81908f58b0a3be090ef0".
        project_resource_id: Optional Azure resource id of the Foundry
            project the evaluation belongs to. Required by Microsoft systems
            when you want the evaluation linked to a specific project.
            Example: "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<acct>/projects/<proj>".
        enduser_id: Optional signed-in user identity (e.g., Entra ID object
            id, email). This is PII and lands in App Insights as
            `user_AuthenticatedId`.
            Examples: "alice@contoso.com", "241964ad-a8db-4318-9f2e-5a7dc1f05349".
        enduser_pseudo_id: Optional random, non-identifying id you generated
            (e.g., a browser cookie or device id). Use when the user is
            anonymous or you don't want to log PII. Lands in App Insights
            as `user_Id`.
            Example: "sess_QdH5CAWJgqVT4rOr0qtumf".
        tags: Optional extra metadata to attach to the event. Each key is
            emitted as `microsoft.human_evaluation.tags.<key>` so you can
            slice on it later in App Insights.
            Example: {"subscription_tier": "basic_plan", "feature": "chat"}.
        evaluation_id: Optional stable id for this specific evaluation event,
            useful if you want to update or correlate it later. Defaults to a
            fresh uuid4.
            Example: "69d937a7-32e2-412e-97c9-119e2d282723".
    """
    if kind not in _KIND_DEFAULTS:
        raise ValueError(f"Unsupported kind '{kind}'. Use 'binary' or 'likert_5'.")
    defaults = _KIND_DEFAULTS[kind]

    if not defaults["min_value"] <= score_value <= defaults["max_value"]:
        raise ValueError(
            f"score_value {score_value} is outside the allowed range "
            f"[{defaults['min_value']}, {defaults['max_value']}] for kind '{kind}'."
        )

    # Ensure scores are whole numbers
    if score_value != int(score_value):
        raise ValueError(
            f"score_value {score_value} must be a whole number (no fractional part) "
            f"for kind '{kind}'."
        )

    # Per spec, the score is at or above the threshold = "pass", below = "fail".
    # (Binary: 1.0 -> pass, 0.0 -> fail. Likert-5: >=3.0 -> pass, <3.0 -> fail.)
    score_label = "pass" if score_value >= defaults["threshold"] else "fail"

    # `internal_properties` carries Microsoft-specific attributes. It MUST be a
    # JSON-encoded string (not a nested object) to match how downstream systems
    # like Azure Monitor and Foundry consume it.
    internal_properties = {
        "gen_ai.evaluation.threshold": str(defaults["threshold"]),
        "gen_ai.evaluation.min_value": str(defaults["min_value"]),
        "gen_ai.evaluation.max_value": str(defaults["max_value"]),
        "gen_ai.evaluation.desirable_direction": defaults["desirable_direction"],
        "gen_ai.evaluation.type": defaults["type"],
        "microsoft.human_evaluation.source": "end_user",
        "microsoft.human_evaluation.kind": kind,
        "microsoft.human_evaluation.id": evaluation_id or str(uuid.uuid4()),
    }
    if project_resource_id:
        internal_properties["gen_ai.azure_ai_project.id"] = project_resource_id
    if response_id:
        internal_properties["gen_ai.response.id.type"] = "responses"
    if tags:
        for tag_name, tag_value in tags.items():
            internal_properties[f"microsoft.human_evaluation.tags.{tag_name}"] = tag_value

    # Top-level event attributes follow the OTel `gen_ai.evaluation.result`
    # event shape (except internal_properties). `microsoft.custom_event.name` 
    # is what routes the record to the `customEvents` App Insights table.
    attributes = {
        "microsoft.custom_event.name": "gen_ai.evaluation.result",
        "gen_ai.evaluation.name": evaluation_name,
        "gen_ai.evaluation.score.value": score_value,
        "gen_ai.evaluation.score.label": score_label,
        "internal_properties": json.dumps(internal_properties),
    }
    if explanation is not None:
        attributes["gen_ai.evaluation.explanation"] = explanation
    if response_id is not None:
        attributes["gen_ai.response.id"] = response_id
    if enduser_id is not None:
        attributes["enduser.id"] = enduser_id
    if enduser_pseudo_id is not None:
        attributes["enduser.pseudo.id"] = enduser_pseudo_id

    logger.info("gen_ai.evaluation.result", extra=attributes)


if __name__ == "__main__":
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        # Pull the Application Insights connection string attached to your Foundry
        # project and wire OpenTelemetry up to it. All `logger.info(...)` calls
        # below will be exported to Application Insights.
        connection_string = project_client.telemetry.get_application_insights_connection_string()

        configure_azure_monitor(connection_string=connection_string)

        # Optional: Derive the Foundry Project's resource id from any connection. The
        # endpoint URL alone only gives us the account + project names, but every
        # Connection's `id` is a full ARM path of the form:
        #   /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<acct>/projects/<proj>/connections/<name>
        # We just strip the trailing /connections/<name> to get the project id.
        any_connection = next(iter(project_client.connections.list()), None)
        project_resource_id = (
            any_connection.id.rsplit("/connections/", 1)[0] if any_connection else None
        )

        # The two examples below differ in evaluation kind (binary vs likert_5)
        # AND in how the end user is identified, just to show both styles. In your
        # own app, those two choices are independent. You can also pass both
        # `enduser_id` and `enduser_pseudo_id` together -- typical for a
        # signed-in user whose browser you've been tracking with a cookie.

        # Example 1: A signed-in end user gives a thumbs up on the agent's task
        # completion.
        emit_human_evaluation_event(
            evaluation_name="task_completion",
            score_value=1.0,
            kind="binary",
            explanation="The agent provided accurate weather information as requested.",
            response_id="resp_64904952b20872620069f8d600779c81908f58b0a3be090ef0",
            project_resource_id=project_resource_id,
            enduser_id="241964ad-a8db-4318-9f2e-5a7dc1f05349",
            tags={"subscription_tier": "basic_plan"},
        )
        print("Emitted binary human evaluation event.")

        # Example 2: An anonymous end user rates the agent's response 4 out of 5
        # stars for relevance.
        emit_human_evaluation_event(
            evaluation_name="relevance",
            score_value=4.0,
            kind="likert_5",
            explanation="The agent's response is relevant to the query.",
            response_id="resp_1234567890abcdef",
            project_resource_id=project_resource_id,
            enduser_pseudo_id="sess_QdH5CAWJgqVT4rOr0qtumf",
            tags={"subscription_tier": "free_plan"},
        )
        print("Emitted likert_5 human evaluation event.")
