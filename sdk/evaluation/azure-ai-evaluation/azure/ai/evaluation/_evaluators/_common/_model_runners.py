# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model runners execute a prepared request against a model backend.

A runner owns backend configuration, authentication and transport. It never interprets a model's answer
as an evaluator score; that stays with the evaluator.
"""

import asyncio
import inspect
import ipaddress
import json
import logging
import math
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy, CustomHookPolicy
from azure.core.pipeline.transport import AioHttpTransport

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from ..._common.utils import construct_prompty_model_config, validate_model_config
from ..._http_utils import get_async_http_client
from ._decision_protocols import DECISION_PROTOCOLS, REFUSAL, DecisionProtocol

if os.getenv("AI_EVALS_USE_PF_PROMPTY", "false").lower() == "true":
    from promptflow.core._flow import AsyncPrompty
else:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty

try:
    from ..._user_agent import UserAgentSingleton
except ImportError:

    class UserAgentSingleton:  # type: ignore[no-redef]
        @property
        def value(self) -> str:
            return "None"


DECISION_MODEL_TYPE = "decision"
_DECISION_TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"
_DECISION_RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504, 529]
LOGGER = logging.getLogger(__name__)
_PREFIX = "azure.ai.evaluation.decision."
_DECISION_CONFIG_KEYS = {
    "type",
    "azure_endpoint",
    "azure_deployment",
    "api_key",
    "credential",
    "probability_threshold",
    "decision_protocol",
}
_DEFAULT_PROBABILITY_THRESHOLD = 0.75
_DEFAULT_PROTOCOL = "microsoft"
_INVALID_EVIDENCE = "Decision evidence must be finite JSON-serializable data."
# The provider error code, and failed-row error kind, of a content filter rejecting the evaluated content.
CONTENT_FILTER = "content_filter"
# Set on the EvaluationException raised when the cancellation callback stops a request. Unlike the execution
# summary, which is omitted when it exceeds the hosted metadata bounds, it is always present.
CANCELLED_BY_CALLBACK = "_decision_cancelled_by_callback"
# The service adds api_version to every resolved model configuration; the decision endpoint does not use it.
_IGNORED_CONFIG_KEYS = {"api_version"}
_USAGE_DETAIL_FIELDS = (
    ("input_tokens_details", ("cached_tokens", "cache_write_tokens")),
    ("output_tokens_details", ("reasoning_tokens",)),
)


def is_decision_model_config(model_config: Any) -> bool:
    """Whether a model configuration explicitly selects a decision model.

    :param model_config: The model configuration passed to an evaluator.
    :type model_config: Any
    :return: True only for configurations tagged ``type="decision"``.
    :rtype: bool
    """
    return isinstance(model_config, dict) and model_config.get("type") == DECISION_MODEL_TYPE


def _integer(value: Any, maximum: Optional[int] = None) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool) and 0 <= value and (maximum is None or value <= maximum)
    )


def _utf8_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def usage_details(usage: Any) -> Dict[str, Dict[str, int]]:
    """Return the known cache and reasoning counters of a provider usage object.

    For example, ``{"input_tokens": 12, "input_tokens_details": {"cached_tokens": 4}}`` yields
    ``{"input_tokens_details": {"cached_tokens": 4}}``. The counters describe part of the input or output tokens and
    are never added to token totals; counters that are not nonnegative integers are omitted.

    :param usage: The untrusted provider usage object.
    :type usage: Any
    :return: Known counters grouped like the provider's usage object.
    :rtype: Dict[str, Dict[str, int]]
    """
    details: Dict[str, Dict[str, int]] = {}
    if isinstance(usage, dict):
        for group, fields in _USAGE_DETAIL_FIELDS:
            values = usage.get(group)
            if isinstance(values, dict):
                known = {field: values[field] for field in fields if _integer(values.get(field))}
                if known:
                    details[group] = known
    return details


def validated_execution(value: Any) -> Optional[Dict[str, Any]]:
    """Copy only a complete, strictly typed shared or independent execution summary.

    :param value: The untrusted summary carrier.
    :type value: Any
    :return: Known validated fields, or None for an invalid carrier.
    :rtype: Optional[Dict[str, Any]]
    """
    if not isinstance(value, dict):
        return None
    if "operation_id" in value:
        keys = {
            "operation_id",
            "attempt_count",
            "unknown_usage_attempt_count",
            "result_usage_scope",
            "usage_completeness",
        }
        if set(value) != keys or not all(
            (
                isinstance(value["operation_id"], str)
                and re.fullmatch("[0-9a-f]{32}", value["operation_id"]) is not None,
                _integer(value["attempt_count"]),
                _integer(value["unknown_usage_attempt_count"]),
                value["result_usage_scope"] == "final_response_only",
                value["usage_completeness"]
                in ("all_attempts_reported", "some_attempts_reported", "no_attempts_reported"),
            )
        ):
            return None
        return dict(value)
    keys = {"attempt_count", "retry_count", "elapsed_ms", "outcome", "last_http_status", "usage_state"}
    elapsed = value.get("elapsed_ms")
    status = value.get("last_http_status")
    if (
        not keys - {"last_http_status"} <= value.keys()
        or isinstance(elapsed, bool)
        or not isinstance(elapsed, (int, float))
    ):
        return None
    if not all(
        (
            _integer(value["attempt_count"], 21),
            _integer(value["retry_count"], 20),
            0 <= elapsed <= 86400000 and math.isfinite(elapsed),
            value["outcome"] in ("completed", "error", "deadline", "cancelled"),
            value["usage_state"] in ("known", "partial", "unknown"),
            status is None or (_integer(status, 599) and status >= 100),
        )
    ):
        return None
    return {key: value.get(key) for key in keys}


def _diagnostic(message: str) -> None:
    # Observer failures must not replace a model result, even if diagnostic logging is also broken.
    try:
        LOGGER.warning(message)
    except Exception:  # pylint: disable=broad-except
        pass


class DecisionExecution(CustomHookPolicy):
    """One operation's per-attempt pipeline policy; never shared between concurrent calls."""

    def __init__(self, logger: Any, max_response_bytes: Optional[int], protocol: str = _DEFAULT_PROTOCOL) -> None:
        super().__init__()
        self.logger = logger
        self.max_response_bytes = max_response_bytes
        self.protocol = protocol
        self.started = time.monotonic()
        self.attempt_started: Optional[float] = None
        self.attempt_count = 0
        self.known_usage_attempts = 0
        self.partial_usage_attempts = 0
        self.last_http_status: Optional[int] = None
        self.outcome = "error"
        self.instruments: Optional[Dict[str, Any]] = None

    def on_request(self, request: Any) -> None:
        self.attempt_count += 1
        self.attempt_started = time.monotonic()
        super().on_request(request)

    def on_response(self, request: Any, response: Any) -> None:
        raw = response.http_response
        status = raw.status_code
        self.last_http_status = status if _integer(status, 599) and status >= 100 else None
        known = False
        partial = False
        try:
            body = raw.body()
            if self.max_response_bytes is None or len(body) <= self.max_response_bytes:
                payload = json.loads(body)
                usage = payload.get("usage") if isinstance(payload, dict) else None
                if isinstance(usage, dict):
                    tokens = [_integer(usage.get(key)) for key in ("input_tokens", "output_tokens")]
                    known, partial = all(tokens), any(tokens)
        except (ValueError, TypeError):
            pass
        self.known_usage_attempts += int(known)
        self.partial_usage_attempts += int(partial and not known)
        self.finish_attempt(
            "completed" if status == 200 else "error",
            "known" if known else "partial" if partial else "unknown",
            self.last_http_status,
        )
        super().on_response(request, response)

    def on_exception(self, request: Any) -> None:
        self.finish_attempt("error")

    def summary(self, outcome: str) -> Dict[str, Any]:
        return {
            "attempt_count": self.attempt_count,
            "retry_count": max(0, self.attempt_count - 1),
            "elapsed_ms": (time.monotonic() - self.started) * 1000,
            "outcome": outcome,
            "last_http_status": self.last_http_status,
            "usage_state": (
                "known"
                if self.attempt_count and self.known_usage_attempts == self.attempt_count
                else "partial" if self.known_usage_attempts or self.partial_usage_attempts else "unknown"
            ),
        }

    def finish_attempt(self, outcome: str, usage: str = "unknown", status: Optional[int] = None) -> None:
        if self.attempt_started is None:
            return
        elapsed = (time.monotonic() - self.attempt_started) * 1000
        self.attempt_started = None
        self.emit("attempt", outcome, self.summary(outcome), elapsed, usage, status)

    def finish(self, outcome: str) -> Optional[Dict[str, Any]]:
        self.finish_attempt(outcome)
        summary = self.summary(outcome)
        self.emit("execution", outcome, summary, summary["elapsed_ms"], summary["usage_state"])
        accepted = validated_execution(summary)
        if accepted is None:
            _diagnostic("Decision execution summary exceeds the hosted metadata bounds; summary omitted.")
        return accepted

    def emit(
        self,
        phase: str,
        outcome: str,
        summary: Dict[str, Any],
        elapsed: float,
        usage: str,
        status: Optional[int] = None,
    ) -> None:
        status = self.last_http_status if phase == "execution" else status
        dimensions = {
            "backend": "decision",
            "route": "shared_sdk",
            "protocol": self.protocol,
            "phase": phase,
            "outcome": outcome,
            "usage_state": usage,
            "http_status_class": f"{status // 100}xx" if status is not None else "unknown",
            "throttled": str(status == 429).lower(),
        }
        try:
            logger = self.logger
            if logger is not None and logger.isEnabledFor(logging.INFO):
                fields = {
                    "decision_dimensions": json.dumps(dimensions),
                    "decision_execution": json.dumps(summary),
                }
                while isinstance(logger, logging.LoggerAdapter):
                    # Python 3.10 LoggerAdapter.process replaces, rather than merges, per-call extra fields.
                    _, kwargs = logger.process("DECISION_EXECUTION_OBSERVATION", {"extra": dict(fields)})
                    fields = {**kwargs.get("extra", {}), **fields}
                    logger = logger.logger
                logger.info("DECISION_EXECUTION_OBSERVATION", extra=fields)
        except Exception:  # pylint: disable=broad-except
            _diagnostic("Decision execution log sink failed; evaluation and metrics continue.")
        try:
            self.emit_metrics(phase, elapsed, dimensions)
        except Exception:  # pylint: disable=broad-except
            _diagnostic("Decision execution metric sink failed; evaluation and logs continue.")

    def emit_metrics(self, phase: str, elapsed: float, dimensions: Dict[str, str]) -> None:
        if self.instruments is None:
            try:
                from opentelemetry.metrics import get_meter  # pylint: disable=import-outside-toplevel
            except ImportError:
                self.instruments = {}
                LOGGER.debug("Decision metrics require the optional opentelemetry extra.")
                return
            meter = get_meter("azure.ai.evaluation.decision")
            self.instruments = {
                key: meter.create_counter(_PREFIX + key)
                for key in ("provider.attempts", "provider.retries", "operations")
            }
            self.instruments["provider.duration"] = meter.create_histogram(_PREFIX + "provider.duration", unit="ms")
        if not self.instruments:
            return
        if phase == "attempt":
            self.instruments["provider.attempts"].add(1, attributes=dimensions)
            self.instruments["provider.duration"].record(elapsed, attributes=dimensions)
            if self.attempt_count > 1:
                self.instruments["provider.retries"].add(1, attributes=dimensions)
        else:
            self.instruments["operations"].add(1, attributes=dimensions)


class PromptyModelRunner:
    """Loads a Prompty flow for a chat model and invokes it without interpreting the output."""

    def __init__(
        self,
        *,
        model_config: dict,
        prompty_file: str,
        credential: Any = None,
        is_reasoning_model: bool = False,
        evaluator_name: str,
        api_version: str,
    ) -> None:
        user_agent = f"{UserAgentSingleton().value} (type=evaluator subtype={evaluator_name})"
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config), api_version, user_agent
        )
        self.flow = AsyncPrompty.load(
            source=prompty_file,
            model=prompty_model_config,
            token_credential=credential,
            is_reasoning_model=is_reasoning_model,
        )

    async def __call__(self, *, timeout: float, **eval_input: Any) -> Dict[str, Any]:
        return await self.flow(timeout=timeout, **eval_input)


def _invalid_config(message: str) -> EvaluationException:
    return EvaluationException(
        message=message,
        internal_message=message,
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=ErrorTarget.EVALUATE,
    )


def _failed(message: str, blame: ErrorBlame = ErrorBlame.SYSTEM_ERROR) -> EvaluationException:
    return EvaluationException(
        message=message,
        internal_message=message,
        blame=blame,
        category=ErrorCategory.FAILED_EXECUTION,
        target=ErrorTarget.EVALUATE,
    )


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _probability(value: Any) -> float:
    if not _is_finite_number(value):
        raise ValueError("Decision probabilities must be finite numbers.")
    if not 0 <= value <= 1:
        raise ValueError("Decision probabilities must be in [0, 1].")
    return float(value)


def validate_noul_answer(answer: Dict[str, Any]) -> float:
    """Return the probability of a ``noul`` answer.

    :param answer: The answer for a ``noul`` question.
    :type answer: Dict[str, Any]
    :return: The probability that the condition holds.
    :rtype: float
    :raises ValueError: If the probability is missing, non-finite or outside [0, 1].
    """
    return _probability(answer.get("noul"))


def validate_score_answer(answer: Dict[str, Any], levels: int) -> List[float]:
    """Return the level probabilities of a ``score`` answer after validating its fields.

    Hundredth-precision probabilities allow rounding error of ``0.005`` per level plus ``1e-12``.
    Other distributions must sum to one within an absolute tolerance of ``0.001``.
    The native mean is checked for finiteness, not consistency with the distribution.

    :param answer: The answer for a ``score`` question.
    :type answer: Dict[str, Any]
    :param levels: The number of levels in the question's scale.
    :type levels: int
    :return: The probability of each level, lowest level first.
    :rtype: List[float]
    :raises ValueError: If the probabilities, mean or confidence are missing or malformed.
    """
    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != {str(i) for i in range(levels)}:
        raise ValueError(f"a score answer requires probabilities for exactly {levels} levels.")
    distribution = [_probability(probabilities[str(i)]) for i in range(levels)]
    tolerance = len(distribution) * 0.005 + 1e-12 if all(value == round(value, 2) for value in distribution) else 0.001
    if not math.isclose(math.fsum(distribution), 1.0, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError("score probabilities must sum to one within the precision-aware rounding tolerance.")
    mean = answer.get("score")
    if not _is_finite_number(mean):
        raise ValueError("the score mean must be finite.")
    _probability(answer.get("confidence"))
    return distribution


class DecisionModelRunner:
    """Sends prepared evidence and typed questions to a Decision deployment in Foundry.

    The model configuration must be tagged ``type="decision"`` and contain the Foundry resource endpoint
    (``azure_endpoint``) and the deployment name (``azure_deployment``). Authentication uses ``api_key`` when
    present, otherwise an explicitly supplied Entra credential (from ``credential`` in the configuration or the
    constructor). No default credential is created for Decision. The endpoint must use HTTPS;
    HTTP is permitted only for localhost or loopback IP literals.
    Caller-supplied credentials remain caller-owned. ``api_version`` is accepted and ignored.
    Reuse a synchronous ``azure.identity.DefaultAzureCredential`` for public synchronous and batch calls,
    and close it after all calls complete. Async credentials require a caller-managed event loop and must
    only be reused on that loop; cross-loop reuse is not supported.
    ``probability_threshold`` (default 0.75) is only accepted when ``binary=True``.

    ``decision_protocol`` selects the provider contract: the default ``"microsoft"`` uses the Microsoft Decision
    operation, and ``"openai"`` uses Azure OpenAI's ``/openai/v1/decisions`` operation, which requires a deployment
    with the Decision capability in a supported region. Model names never select a protocol. Every protocol returns
    the same answers keyed by question identifier, so evaluators score them with the same policies. An OpenAI
    question can be refused; the refusal fails an evaluation only when that evaluation reads the refused answer.

    ``azure_endpoint`` must be the account resource root, not a project endpoint.
    For example, use ``https://account.services.ai.azure.com`` rather than a URL ending in
    ``/api/projects/project``. OpenAI requires the account's OpenAI endpoint, such as
    ``https://account.openai.azure.com``, optionally with its ``/openai`` or ``/openai/v1`` base path;
    the Microsoft protocol retains a supplied path when appending the provider operation.

    Execution controls are keyword-only and separate from model configuration. ``timeout_seconds`` bounds
    each connect/read; the call's ``timeout`` limits authentication, retries and response body reading.
    Decision requests use the native async HTTP transport so timeout and cancellation stop body reads.
    An injected pipeline retains its own transport; that transport must support cancellation for the same guarantee.
    ``max_retries`` defaults to 3. ``cancellation_requested`` is polled every 50 ms, including retry waits;
    it stops awaiting synchronous credentials but cannot stop their worker threads. Byte limits measure the
    compact unescaped UTF-8 JSON of the canonical request ``{"model", "state", "questions"}`` before protocol
    encoding, so every protocol admits the same evidence; ``max_state_question_bytes`` applies to the largest
    individual ``{"state", "question"}`` pair. ``max_response_bytes`` limits acceptance before parsing,
    not transport allocation.
    """

    SUPPORTED_PROTOCOLS = frozenset(DECISION_PROTOCOLS)

    def __init__(
        self,
        model_config: dict,
        credential: Any = None,
        *,
        binary: bool = False,
        evaluator_name: str = "DecisionModelRunner",
        timeout_seconds: Optional[float] = None,
        max_retries: int = 3,
        cancellation_requested: Optional[Callable[[], bool]] = None,
        max_request_bytes: Optional[int] = None,
        max_state_question_bytes: Optional[int] = None,
        max_response_bytes: Optional[int] = None,
    ) -> None:
        if timeout_seconds is not None and (not _is_finite_number(timeout_seconds) or timeout_seconds <= 0):
            raise _invalid_config("'timeout_seconds' must be a positive finite number.")
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise _invalid_config("'max_retries' must be a nonnegative integer.")
        for name, value in (
            ("max_request_bytes", max_request_bytes),
            ("max_state_question_bytes", max_state_question_bytes),
            ("max_response_bytes", max_response_bytes),
        ):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
                raise _invalid_config(f"'{name}' must be a positive integer.")
        if cancellation_requested is not None and not callable(cancellation_requested):
            raise _invalid_config("'cancellation_requested' must be callable.")
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._cancellation_requested = cancellation_requested
        self._max_request_bytes = max_request_bytes
        self._max_state_question_bytes = max_state_question_bytes
        self._max_response_bytes = max_response_bytes
        if not is_decision_model_config(model_config):
            raise _invalid_config(f"A decision model configuration must be a dict with type '{DECISION_MODEL_TYPE}'.")
        unexpected = set(model_config) - _DECISION_CONFIG_KEYS - _IGNORED_CONFIG_KEYS
        if unexpected:
            raise _invalid_config(f"Unsupported decision model configuration fields: {sorted(unexpected)}.")

        endpoint = model_config.get("azure_endpoint")
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise _invalid_config("'azure_endpoint' must be a nonempty string.")
        try:
            parsed = urlsplit(endpoint)
            hostname = parsed.hostname
            port = parsed.port
            loopback = hostname == "localhost"
            if hostname and not loopback:
                try:
                    loopback = ipaddress.ip_address(hostname).is_loopback
                except ValueError:
                    labels = hostname.rstrip(".").encode("idna").decode("ascii").split(".")
                    if any(
                        not label
                        or not label[0].isalnum()
                        or not label[-1].isalnum()
                        or not all(character.isalnum() or character == "-" for character in label)
                        for label in labels
                    ):
                        raise ValueError
            if (
                any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in endpoint)
                or "\\" in endpoint
                or not hostname
                or "%" in hostname
                or parsed.netloc.endswith(":")
                or parsed.username is not None
                or parsed.password is not None
                or "?" in endpoint
                or "#" in endpoint
                or (port is not None and port == 0)
                or (parsed.scheme != "https" and not (parsed.scheme == "http" and loopback))
            ):
                raise ValueError
        except ValueError:
            raise _invalid_config(
                "'azure_endpoint' must be a valid HTTPS URL; HTTP is allowed only for loopback."
            ) from None
        deployment = model_config.get("azure_deployment")
        if not isinstance(deployment, str) or not deployment.strip():
            raise _invalid_config("'azure_deployment' must be the decision model deployment name.")
        api_key = model_config.get("api_key")
        if api_key is not None and (not isinstance(api_key, str) or not api_key.strip()):
            raise _invalid_config("'api_key' must be a nonempty string.")

        # Like the Prompty path, an API key wins; a credential is only used when there is no key.
        credential = credential if credential is not None else model_config.get("credential")
        if not api_key and not callable(getattr(credential, "get_token", None)):
            raise _invalid_config("Decision models require an 'api_key' or a credential with a callable 'get_token'.")
        self._credential: Any = None if api_key else credential

        threshold = model_config.get("probability_threshold", _DEFAULT_PROBABILITY_THRESHOLD)
        if "probability_threshold" in model_config and not binary:
            raise _invalid_config("'probability_threshold' is only supported by binary evaluators.")
        try:
            self.probability_threshold = _probability(threshold)
        except ValueError:
            raise _invalid_config("'probability_threshold' must be a number in [0, 1].") from None

        protocol = model_config.get("decision_protocol", _DEFAULT_PROTOCOL)
        if not isinstance(protocol, str) or protocol not in DECISION_PROTOCOLS:
            raise _invalid_config(f"'decision_protocol' must be one of {sorted(DECISION_PROTOCOLS)}.")
        self._protocol: DecisionProtocol = DECISION_PROTOCOLS[protocol]
        try:
            self._url = self._protocol.operation_url(endpoint)
        except ValueError as exc:
            raise _invalid_config(str(exc)) from None
        self._deployment = deployment
        self._api_key = api_key
        self._user_agent = f"{UserAgentSingleton().value} (type=evaluator subtype={evaluator_name})"
        self._execution_logger: Any = logging.getLogger(__name__)

    def _bind_execution_logger(self, logger: Any) -> None:
        """Bind a host's context-aware logger without changing transport or credential ownership.

        :param logger: The host logger or LoggerAdapter; None disables execution logs, not metrics.
        :type logger: Any
        """
        self._execution_logger = logger

    @property
    def deployment(self) -> str:
        """The deployment name sent as the request's model."""
        return self._deployment

    @property
    def decision_protocol(self) -> str:
        """The provider protocol, for example ``"microsoft"`` or ``"openai"``."""
        return self._protocol.name

    async def __call__(self, *, state: Any, questions: Dict[str, Dict[str, Any]], timeout: float) -> Dict[str, Any]:
        """Request the decisions for ``questions`` about ``state`` and return the validated response.

        :keyword state: The prepared evidence, as text or JSON-serializable data.
        :paramtype state: Any
        :keyword questions: Typed questions keyed by identifier; ``noul`` and ``score`` are supported.
        :paramtype questions: Dict[str, Dict[str, Any]]
        :keyword timeout: Overall time limit in seconds.
        :paramtype timeout: float
        :return: ``{"model", "answers", "usage", "usage_details"}`` with answers keyed by question identifier and
            the response's structure checked against the questions.
        :rtype: Dict[str, Any]
        """
        if not _is_finite_number(timeout) or timeout <= 0:
            raise _invalid_config("'timeout' must be a positive finite number.")
        deadline = time.monotonic() + timeout
        execution = DecisionExecution(self._execution_logger, self._max_response_bytes, self.decision_protocol)
        outcome = "error"
        properties = self._response_properties(None)
        try:
            for question in questions.values():
                if question.get("type") not in ("noul", "score"):
                    raise _invalid_config(f"Decision question type '{question.get('type')}' is not supported.")
            # Budgets bound the evidence and questions the model reads, so every protocol measures the same canonical
            # request and admits the same evidence; wire encoding, such as evidence escaped into JSON text, is not read.
            canonical = {"model": self._deployment, "state": state, "questions": questions}
            try:
                request = _utf8_json(canonical)
                state_question_bytes = 0
                if self._max_state_question_bytes is not None:
                    state_question_bytes = max(
                        (len(_utf8_json({"state": state, "question": question})) for question in questions.values()),
                        default=0,
                    )
            except (ValueError, TypeError, OverflowError, UnicodeError):
                raise _failed(_INVALID_EVIDENCE, ErrorBlame.USER_ERROR) from None
            if (self._max_request_bytes is not None and len(request) > self._max_request_bytes) or (
                self._max_state_question_bytes is not None and state_question_bytes > self._max_state_question_bytes
            ):
                raise _failed("The decision request exceeds the configured byte budget.", ErrorBlame.USER_ERROR)
            try:
                body = self._protocol.encode(self._deployment, state, questions)
                # A wire body that is the canonical request, as Microsoft's is, is not serialized again.
                content = request if body == canonical else _utf8_json(body)
            except (ValueError, TypeError, OverflowError, UnicodeError) as exc:
                raise _invalid_config(f"Invalid decision request: {exc}") from None
            try:
                payload = await asyncio.wait_for(
                    self._await_request(content, deadline, execution), timeout=max(0, deadline - time.monotonic())
                )
            except asyncio.TimeoutError:
                outcome = "deadline"
                raise _failed("The decision model request timed out.") from None
            properties = self._response_properties(payload)
            try:
                result = self._validate_response(payload, questions)
            except ValueError as exc:
                raise _failed(f"The decision model returned an invalid response: {exc}") from None
            outcome = "completed"
            return result
        except asyncio.CancelledError as exc:
            outcome = "cancelled"
            setattr(exc, "properties", properties)
            raise
        except EvaluationException as exc:
            if outcome != "deadline":
                outcome = execution.outcome
            if outcome == "cancelled":
                setattr(exc, CANCELLED_BY_CALLBACK, True)
            if exc.properties is None:
                exc.properties = properties
            properties = exc.properties
            raise
        finally:
            summary = execution.finish(outcome)
            if summary is not None:
                if outcome == "completed":
                    result["_decision_execution"] = summary
                else:
                    properties.setdefault("decision_model", {})["execution"] = summary

    def _cancelled(self) -> bool:
        callback = self._cancellation_requested
        if callback is None:
            return False
        try:
            result = callback()
        except Exception:  # pylint: disable=broad-except
            raise _failed("The decision cancellation callback failed.", ErrorBlame.USER_ERROR) from None
        if not isinstance(result, bool):
            raise _failed("The decision cancellation callback must return a boolean.", ErrorBlame.USER_ERROR)
        return result

    async def _await_request(self, content: bytes, deadline: float, execution: DecisionExecution) -> Any:
        if self._cancelled():
            execution.outcome = "cancelled"
            raise _failed("The decision model request was cancelled.", ErrorBlame.USER_ERROR)
        if self._cancellation_requested is None:
            return await self._post(content, deadline=deadline, execution=execution)
        task = asyncio.create_task(self._post(content, deadline=deadline, execution=execution))
        try:
            while not task.done():
                if self._cancelled():
                    execution.outcome = "cancelled"
                    raise _failed("The decision model request was cancelled.", ErrorBlame.USER_ERROR)
                await asyncio.wait({task}, timeout=0.05)
            return await task
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    async def _get_token(self) -> str:
        if inspect.iscoroutinefunction(self._credential.get_token):
            return (await self._credential.get_token(_DECISION_TOKEN_SCOPE)).token
        token = await asyncio.to_thread(self._credential.get_token, _DECISION_TOKEN_SCOPE)
        if inspect.isawaitable(token):
            token = await token
        return token.token

    async def _post(self, content: bytes, *, deadline: float, execution: DecisionExecution) -> Any:
        headers = {"x-ms-useragent": self._user_agent, "Content-Type": "application/json"}
        if self._api_key:
            headers["api-key"] = self._api_key
        else:
            try:
                headers["Authorization"] = f"Bearer {await self._get_token()}"
            except EvaluationException:
                raise
            except Exception:  # pylint: disable=broad-except
                raise _failed("Could not acquire a token for the decision model.", ErrorBlame.USER_ERROR) from None

        policies: Dict[str, Any] = {
            "custom_hook_policy": execution,
            "retry_policy": AsyncRetryPolicy(
                retry_total=self._max_retries,
                retry_connect=self._max_retries,
                retry_read=self._max_retries,
                retry_status=self._max_retries,
                retry_backoff_factor=0.8,
                retry_on_status_codes=_DECISION_RETRY_STATUS_CODES,
            ),
            "redirect_policy": AsyncRedirectPolicy(permit_redirects=False),
        }
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            execution.outcome = "deadline"
            raise _failed("The decision model request timed out.")
        # Native retry policy carries this budget across attempts and clamps the scalar connect/read timeout.
        options: Dict[str, Any] = {
            "retry_on_methods": ["POST"],
            "timeout": remaining,
            "connection_timeout": (
                min(self._timeout_seconds, remaining) if self._timeout_seconds is not None else remaining
            ),
        }
        try:
            async with get_async_http_client(
                transport=AioHttpTransport(read_timeout=options["connection_timeout"])
            ).with_policies(**policies) as client:
                response = await client.post(self._url, content=content, headers=headers, **options)
                status = response.status_code
                content = response.body()
        except EvaluationException:
            raise
        except Exception:  # pylint: disable=broad-except
            if time.monotonic() >= deadline:
                execution.outcome = "deadline"
                raise _failed("The decision model request timed out.") from None
            raise _failed("The decision model request failed; check the endpoint and network access.") from None
        if self._max_response_bytes is not None and len(content) > self._max_response_bytes:
            if status == 200:
                raise _failed("The decision response exceeds the configured byte budget.")
            payload = None
        else:
            try:
                payload = json.loads(content)
            except (ValueError, TypeError):
                if status == 200:
                    raise _failed("The decision model returned invalid JSON.") from None
                payload = None
        if status != 200:
            blame = ErrorBlame.USER_ERROR if status in (400, 401, 403, 404, 422) else ErrorBlame.SYSTEM_ERROR
            provider_error = payload.get("error") if isinstance(payload, dict) else None
            code = provider_error.get("code") if isinstance(provider_error, dict) else None
            diagnostic = (
                f" ({code})"
                if isinstance(code, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", code) is not None
                else ""
            )
            error = _failed(f"The decision model returned HTTP {status}{diagnostic}.", blame)
            error.properties = self._response_properties(payload)
            if code == CONTENT_FILTER:
                # The provider's content filter rejected the evaluated content, not how the request was built.
                error.properties["decision_model"]["error_kind"] = CONTENT_FILTER
            raise error
        return payload

    def _response_properties(self, payload: Any) -> Dict[str, Any]:
        """Retain only independently known final-response usage, never raw answers or retry totals."""
        properties: Dict[str, Any] = {
            "decision_model": {"deployment": self._deployment, "protocol": self.decision_protocol}
        }
        usage = payload.get("usage") if isinstance(payload, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        details = usage_details(usage)
        if details:
            properties["decision_model"]["usage_details"] = details
        for native_key, key in (("input_tokens", "prompt_tokens"), ("output_tokens", "completion_tokens")):
            value = usage.get(native_key)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                properties[key] = value
        if "prompt_tokens" in properties and "completion_tokens" in properties:
            properties["total_tokens"] = properties["prompt_tokens"] + properties["completion_tokens"]
        model = payload.get("model") if isinstance(payload, dict) else None
        if isinstance(model, str) and model.strip():
            properties["model"] = model
        return properties

    def _validate_response(self, payload: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        # Only the response's structure is checked here; answer values are validated by the evaluator when it reads
        # them, so a skipped evaluation never depends on an unusable or refused score.
        if not isinstance(payload, dict):
            raise ValueError("answers are missing.")
        answers = self._protocol.bind_answers(payload, questions)
        if set(answers) != set(questions):
            raise ValueError("answer identifiers do not match the questions.")
        for question_id, question in questions.items():
            answer = answers[question_id]
            answer_type = answer.get("type") if isinstance(answer, dict) else None
            refused = answer_type == REFUSAL and self._protocol.supports_refusals
            if answer_type != question.get("type") and not refused:
                raise ValueError(f"answer '{question_id}' does not match its question type.")

        usage = payload.get("usage")
        if not isinstance(usage, dict):
            raise ValueError("usage is missing.")
        for name in ("input_tokens", "output_tokens"):
            if isinstance(usage.get(name), bool) or not isinstance(usage.get(name), int) or usage[name] < 0:
                raise ValueError("usage must contain nonnegative integer token counts.")
        model = payload.get("model")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("the model identifier is missing.")
        return {
            "model": model,
            "answers": answers,
            "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]},
            "usage_details": usage_details(usage),
        }
