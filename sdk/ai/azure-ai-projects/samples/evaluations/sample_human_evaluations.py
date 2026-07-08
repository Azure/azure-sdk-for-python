# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to emit human evaluation events from your
    application as OpenTelemetry custom events that land in the `customEvents`
    Application Insights table connected to your Microsoft Foundry project.

    Human evaluations capture signals that automated evaluators struggle with,
    such as tone, user satisfaction, and factual nuance. The helpers below emit
    the `gen_ai.evaluation.result` event shape used by Microsoft Foundry:

    * `emit_boolean_evaluation(...)` emits binary scores such as thumbs up/down.
    * `emit_5_point_ordinal_evaluation(...)` emits 1-5 ordered scores such as a
      Likert or star rating.

    Both public helpers call the shared `_emit_human_evaluation(...)` helper so
    the OpenTelemetry and Microsoft-specific attribute mapping stays consistent.
    This sample covers human evaluations submitted by end users of your
    application and correlates evaluation events to OpenAI Responses API response
    IDs when a response ID is provided.

    NOTE: Human evaluations are in preview and carry the risk of breaking
    changes.

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
from typing import Literal, Mapping, Optional

# NOTE: Azure SDK / Application Insights imports (azure-identity,
# azure-monitor-opentelemetry, azure-ai-projects, python-dotenv) are
# intentionally deferred into the `if __name__ == "__main__":` block at the
# bottom of this file. They are only needed when running the sample directly;
# the helper functions remain importable in test environments that do not install
# the full OTel stack. The trace-context imports are only needed when a saved
# trace ID and span ID are provided.

# `configure_azure_monitor` (called in __main__) installs an OpenTelemetry
# LoggingHandler on the root logger, so any standard Python `logging` call below
# this point flows through OTel to Application Insights as a log record. The
# `microsoft.custom_event.name` attribute routes the record to the
# `customEvents` table.
logger = logging.getLogger("human_evaluations")
logger.setLevel(logging.INFO)

EvaluationType = Literal["boolean", "ordinal"]
DesirableDirection = Literal["increase", "decrease"]


def _validate_hex_id(*, name: str, value: str, length: int) -> int:
    if len(value) != length:
        raise ValueError(f"{name} must be a {length}-character hexadecimal string.")

    try:
        parsed_value = int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a {length}-character hexadecimal string.") from exc

    if parsed_value == 0:
        raise ValueError(f"{name} cannot be all zeros.")

    return parsed_value


def _log_evaluation_event(
    *,
    attributes: Mapping[str, object],
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
) -> None:
    if trace_id is None and span_id is None:
        logger.info("gen_ai.evaluation.result", extra=attributes)
        return
    if trace_id is None or span_id is None:
        raise ValueError("trace_id and span_id must be provided together.")

    trace_id_int = _validate_hex_id(name="trace_id", value=trace_id, length=32)
    span_id_int = _validate_hex_id(name="span_id", value=span_id, length=16)

    from opentelemetry import context as otel_context
    from opentelemetry import trace
    from opentelemetry.trace import (
        NonRecordingSpan,
        SpanContext,
        TraceFlags,
        TraceState,
    )

    span_context = SpanContext(
        trace_id=trace_id_int,
        span_id=span_id_int,
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=TraceState(),
    )
    token = otel_context.attach(trace.set_span_in_context(NonRecordingSpan(span_context)))
    try:
        logger.info("gen_ai.evaluation.result", extra=attributes)
    finally:
        otel_context.detach(token)


def _validate_score(
    *,
    score_value: float,
    min_value: float,
    max_value: float,
    evaluation_type: EvaluationType,
) -> float:
    score_value = float(score_value)
    if not (min_value <= score_value <= max_value):
        raise ValueError(
            f"score_value {score_value} is outside the allowed range "
            f"[{min_value}, {max_value}] for evaluation type '{evaluation_type}'."
        )
    if score_value != int(score_value):
        raise ValueError(
            f"score_value {score_value} must be a double-encoded integer value "
            f"for evaluation type '{evaluation_type}'."
        )
    return score_value


def _get_score_label(
    *,
    score_value: float,
    threshold: float,
    desirable_direction: DesirableDirection,
) -> Literal["pass", "fail"]:
    if desirable_direction == "increase":
        return "pass" if score_value >= threshold else "fail"
    if desirable_direction == "decrease":
        return "pass" if score_value <= threshold else "fail"
    raise ValueError(f"Unsupported desirable_direction: {desirable_direction!r}.")


def _emit_human_evaluation(
    *,
    evaluation_metric_name: str,
    score_value: float,
    evaluation_type: EvaluationType,
    min_value: float,
    max_value: float,
    threshold: float,
    desirable_direction: DesirableDirection,
    explanation: Optional[str] = None,
    response_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    project_resource_id: Optional[str] = None,
    enduser_id: Optional[str] = None,
    enduser_pseudo_id: Optional[str] = None,
    tags: Optional[Mapping[str, str]] = None,
    evaluation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
) -> None:
    score_value = _validate_score(
        score_value=score_value,
        min_value=min_value,
        max_value=max_value,
        evaluation_type=evaluation_type,
    )
    score_label = _get_score_label(
        score_value=score_value,
        threshold=threshold,
        desirable_direction=desirable_direction,
    )

    internal_properties = {
        "gen_ai.evaluation.threshold": str(threshold),
        "gen_ai.evaluation.min_value": str(min_value),
        "gen_ai.evaluation.max_value": str(max_value),
        "gen_ai.evaluation.desirable_direction": desirable_direction,
        "gen_ai.evaluation.type": evaluation_type,
    }
    if project_resource_id is not None:
        internal_properties["gen_ai.azure_ai_project.id"] = project_resource_id

    attributes = {
        "microsoft.custom_event.name": "gen_ai.evaluation.result",
        "gen_ai.evaluation.name": evaluation_metric_name,
        "gen_ai.evaluation.score.value": score_value,
        "gen_ai.evaluation.score.label": score_label,
        "microsoft.gen_ai.human_evaluation.source": "end_user",
        "microsoft.gen_ai.evaluation.actor.type": "human",
        "internal_properties": json.dumps(internal_properties),
    }
    if explanation is not None:
        attributes["gen_ai.evaluation.explanation"] = explanation
    if response_id is not None:
        attributes["gen_ai.response.id"] = response_id
    if conversation_id is not None:
        attributes["gen_ai.conversation.id"] = conversation_id
    if enduser_id is not None:
        attributes["enduser.id"] = enduser_id
    if enduser_pseudo_id is not None:
        attributes["enduser.pseudo.id"] = enduser_pseudo_id
    if tags:
        for tag_name, tag_value in tags.items():
            attributes[f"microsoft.gen_ai.evaluation.tags.{tag_name}"] = tag_value
    if evaluation_id is not None:
        attributes["microsoft.gen_ai.human_evaluation.id"] = evaluation_id

    _log_evaluation_event(attributes=attributes, trace_id=trace_id, span_id=span_id)


def emit_boolean_evaluation(
    *,
    evaluation_metric_name: str,
    passed: bool,
    explanation: Optional[str] = None,
    response_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    project_resource_id: Optional[str] = None,
    enduser_id: Optional[str] = None,
    enduser_pseudo_id: Optional[str] = None,
    tags: Optional[Mapping[str, str]] = None,
    evaluation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
) -> None:
    """Emit a boolean human evaluation event.

    Boolean evaluations are typically represented as thumbs up/down, yes/no, or
    pass/fail controls. `passed=True` emits a score of `1.0`; `passed=False`
    emits a score of `0.0`.

    Args:
        evaluation_metric_name: Name of the evaluated metric, such as
            `"task_completion"` or `"helpfulness"`.
        passed: Whether the human evaluation passed.
        explanation: Optional free-form explanation from the end user.
        response_id: Optional OpenAI Responses API response ID being evaluated.
        conversation_id: Optional conversation ID associated with the evaluation.
        project_resource_id: Optional ARM resource ID for the Foundry project.
        enduser_id: Optional signed-in end-user ID. This may contain PII.
        enduser_pseudo_id: Optional pseudonymous end-user ID.
        tags: Optional metadata associated with the evaluation.
        evaluation_id: Optional ID for the evaluation event itself.
        trace_id: Optional trace ID captured when the evaluated response was created.
        span_id: Optional span ID captured when the evaluated response was created.
    """
    _emit_human_evaluation(
        evaluation_metric_name=evaluation_metric_name,
        score_value=1.0 if passed else 0.0,
        evaluation_type="boolean",
        min_value=0.0,
        max_value=1.0,
        threshold=1.0,
        desirable_direction="increase",
        explanation=explanation,
        response_id=response_id,
        conversation_id=conversation_id,
        project_resource_id=project_resource_id,
        enduser_id=enduser_id,
        enduser_pseudo_id=enduser_pseudo_id,
        tags=tags,
        evaluation_id=evaluation_id,
        trace_id=trace_id,
        span_id=span_id,
    )


def emit_5_point_ordinal_evaluation(
    *,
    evaluation_metric_name: str,
    score_value: float,
    threshold: float = 3.0,
    explanation: Optional[str] = None,
    response_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    project_resource_id: Optional[str] = None,
    enduser_id: Optional[str] = None,
    enduser_pseudo_id: Optional[str] = None,
    tags: Optional[Mapping[str, str]] = None,
    evaluation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
) -> None:
    """Emit a 5-point ordinal human evaluation event.

    Ordinal 5-point evaluations use integer scores from `1.0` through `5.0`;
    scores at or above `3.0` are emitted with a `pass` label.

    Args:
        evaluation_metric_name: Name of the evaluated metric, such as
            `"relevance"` or `"helpfulness"`.
        score_value: Integer score from `1.0` through `5.0`.
        threshold: Score at or above this value is passing.
        explanation: Optional free-form explanation from the end user.
        response_id: Optional OpenAI Responses API response ID being evaluated.
        conversation_id: Optional conversation ID associated with the evaluation.
        project_resource_id: Optional ARM resource ID for the Foundry project.
        enduser_id: Optional signed-in end-user ID. This may contain PII.
        enduser_pseudo_id: Optional pseudonymous end-user ID.
        tags: Optional metadata associated with the evaluation.
        evaluation_id: Optional ID for the evaluation event itself.
        trace_id: Optional trace ID captured when the evaluated response was created.
        span_id: Optional span ID captured when the evaluated response was created.
    """
    threshold = float(threshold)
    if not 1.0 <= threshold <= 5.0:
        raise ValueError(f"threshold {threshold} is outside the allowed range [1.0, 5.0].")

    _emit_human_evaluation(
        evaluation_metric_name=evaluation_metric_name,
        score_value=score_value,
        evaluation_type="ordinal",
        min_value=1.0,
        max_value=5.0,
        threshold=threshold,
        desirable_direction="increase",
        explanation=explanation,
        response_id=response_id,
        conversation_id=conversation_id,
        project_resource_id=project_resource_id,
        enduser_id=enduser_id,
        enduser_pseudo_id=enduser_pseudo_id,
        tags=tags,
        evaluation_id=evaluation_id,
        trace_id=trace_id,
        span_id=span_id,
    )


if __name__ == "__main__":
    import os

    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from azure.monitor.opentelemetry import configure_azure_monitor
    from dotenv import load_dotenv

    load_dotenv()

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

        # Optional: derive the Foundry Project's resource id from any connection.
        # The endpoint URL alone only gives us the account + project names, but
        # every Connection's `id` is a full ARM path ending with /connections/<name>.
        any_connection = next(iter(project_client.connections.list()), None)
        project_resource_id = any_connection.id.rsplit("/connections/", 1)[0] if any_connection else None

        # Sample trace and span IDs for demonstration purposes.
        trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
        span_id = "00f067aa0ba902b7"

        # Example 1: an anonymous end user gives a thumbs up on task completion.
        emit_boolean_evaluation(
            evaluation_metric_name="task_completion",
            passed=True,
            explanation="The agent provided accurate weather information as requested.",
            response_id="resp_64904952b20872620069f8d600779c81908f58b0a3be090ef0",
            conversation_id="conv_5j66UpCpwteGg4YSxUnt7lPY",
            project_resource_id=project_resource_id,
            enduser_pseudo_id="sess_123456",
            tags={"subscription_tier": "free_plan"},
            evaluation_id="0b27be45-cd65-4671-ab08-c3eafd4c9613",
            trace_id=trace_id,
            span_id=span_id,
        )
        print("Emitted boolean human evaluation event.")

        # Example 2: a signed-in end user rates relevance on a 5-point scale.
        emit_5_point_ordinal_evaluation(
            evaluation_metric_name="relevance",
            score_value=4.0,
            explanation=(
                "The agent's response is relevant to the query, providing useful "
                "information that addresses the user's intent."
            ),
            response_id="resp_64904952b20872620069f8d600779c81908f58b0a3be090ef0",
            conversation_id="conv_5j66UpCpwteGg4YSxUnt7lPY",
            project_resource_id=project_resource_id,
            enduser_id="oid:241964ad-a8db-4318-9f2e-5a7dc1f05349",
            tags={"department": "marketing"},
            evaluation_id="69d937a7-32e2-412e-97c9-119e2d282723",
            trace_id=trace_id,
            span_id=span_id,
        )
        print("Emitted 5-point ordinal human evaluation event.")
