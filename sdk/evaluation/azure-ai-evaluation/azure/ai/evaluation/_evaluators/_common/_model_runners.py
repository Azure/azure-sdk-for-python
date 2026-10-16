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
import math
import os
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy
from azure.core.pipeline.transport import AioHttpTransport

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from ..._common.utils import construct_prompty_model_config, validate_model_config
from ..._http_utils import get_async_http_client

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
_DECISION_PATH = "/providers/microsoft/v1/systemone"
_DECISION_TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"
_DECISION_RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504, 529]
_DECISION_SAFE_ERROR_CODES = {"DeploymentNotFound"}
_DECISION_CONFIG_KEYS = {
    "type",
    "azure_endpoint",
    "azure_deployment",
    "api_key",
    "credential",
    "probability_threshold",
}
_DEFAULT_PROBABILITY_THRESHOLD = 0.75
_PROBABILITY_SUM_ABS_TOLERANCE = 1e-6
# The service adds api_version to every resolved model configuration; the decision endpoint does not use it.
_IGNORED_CONFIG_KEYS = {"api_version"}


def is_decision_model_config(model_config: Any) -> bool:
    """Whether a model configuration explicitly selects a decision model.

    :param model_config: The model configuration passed to an evaluator.
    :type model_config: Any
    :return: True only for configurations tagged ``type="decision"``.
    :rtype: bool
    """
    return isinstance(model_config, dict) and model_config.get("type") == DECISION_MODEL_TYPE


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


def _probability(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
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

    Probabilities must sum to one within an absolute tolerance of ``1e-6`` for decimal rounding.
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
    if not math.isclose(math.fsum(distribution), 1.0, rel_tol=0.0, abs_tol=_PROBABILITY_SUM_ABS_TOLERANCE):
        raise ValueError("score probabilities must sum to one within an absolute tolerance of 1e-6.")
    mean = answer.get("score")
    if isinstance(mean, bool) or not isinstance(mean, (int, float)) or not math.isfinite(mean):
        raise ValueError("the score mean must be finite.")
    _probability(answer.get("confidence"))
    return distribution


class DecisionModelRunner:
    """Sends prepared evidence and typed questions to a Microsoft-Decision-1 deployment in Foundry.

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

    ``azure_endpoint`` must be the account resource root, not a project or OpenAI API endpoint.
    For example, use ``https://account.services.ai.azure.com`` rather than a URL ending in
    ``/api/projects/project`` or ``/openai``. Any path supplied is retained when appending the provider operation.

    Execution controls are keyword-only and separate from model configuration. ``timeout_seconds`` bounds
    each connect/read; the call's ``timeout`` limits authentication, retries and response body reading.
    Decision requests use the native async HTTP transport so timeout and cancellation stop body reads.
    An injected pipeline retains its own transport; that transport must support cancellation for the same guarantee.
    ``max_retries`` defaults to 3. ``cancellation_requested`` is polled every 50 ms, including retry waits;
    it stops awaiting synchronous credentials but cannot stop their worker threads. Byte limits measure
    compact unescaped UTF-8 JSON, with ``max_state_question_bytes`` applying to the largest individual pair.
    ``max_response_bytes`` limits acceptance before parsing, not transport allocation.
    """

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
        if timeout_seconds is not None and (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
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
        self._credential = None if api_key else credential

        threshold = model_config.get("probability_threshold", _DEFAULT_PROBABILITY_THRESHOLD)
        if "probability_threshold" in model_config and not binary:
            raise _invalid_config("'probability_threshold' is only supported by binary evaluators.")
        try:
            self.probability_threshold = _probability(threshold)
        except ValueError:
            raise _invalid_config("'probability_threshold' must be a number in [0, 1].") from None

        self._url = f"{endpoint.rstrip('/')}{_DECISION_PATH}"
        self._deployment = deployment
        self._api_key = api_key
        self._user_agent = f"{UserAgentSingleton().value} (type=evaluator subtype={evaluator_name})"

    @property
    def deployment(self) -> str:
        """The deployment name sent as the request's model."""
        return self._deployment

    async def __call__(self, *, state: Any, questions: Dict[str, Dict[str, Any]], timeout: float) -> Dict[str, Any]:
        """Request the decisions for ``questions`` about ``state`` and return the validated response.

        :keyword state: The prepared evidence, as text or JSON-serializable data.
        :paramtype state: Any
        :keyword questions: Typed questions keyed by identifier; ``noul`` and ``score`` are supported.
        :paramtype questions: Dict[str, Dict[str, Any]]
        :keyword timeout: Overall time limit in seconds.
        :paramtype timeout: float
        :return: ``{"model", "answers", "usage"}`` with the response's structure checked against the questions.
        :rtype: Dict[str, Any]
        """
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise _invalid_config("'timeout' must be a positive finite number.")
        deadline = time.monotonic() + timeout
        for question in questions.values():
            if question.get("type") not in ("noul", "score"):
                raise _invalid_config(f"Decision question type '{question.get('type')}' is not supported.")
        properties = self._response_properties(None)
        try:
            body = {"model": self._deployment, "state": state, "questions": questions}
            try:
                content = json.dumps(body, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
                state_question_bytes = 0
                if self._max_state_question_bytes is not None:
                    state_question_bytes = max(
                        (
                            len(
                                json.dumps(
                                    {"state": state, "question": question},
                                    ensure_ascii=False,
                                    separators=(",", ":"),
                                    allow_nan=False,
                                ).encode("utf-8")
                            )
                            for question in questions.values()
                        ),
                        default=0,
                    )
            except (ValueError, TypeError, OverflowError, UnicodeError):
                raise _failed(
                    "Decision evidence must be finite JSON-serializable data.", ErrorBlame.USER_ERROR
                ) from None
            if (self._max_request_bytes is not None and len(content) > self._max_request_bytes) or (
                self._max_state_question_bytes is not None and state_question_bytes > self._max_state_question_bytes
            ):
                raise _failed("The decision request exceeds the configured byte budget.", ErrorBlame.USER_ERROR)
            try:
                payload = await asyncio.wait_for(
                    self._await_request(content, deadline), timeout=max(0, deadline - time.monotonic())
                )
            except asyncio.TimeoutError:
                raise _failed("The decision model request timed out.") from None
            properties = self._response_properties(payload)
            try:
                return self._validate_response(payload, questions)
            except ValueError as exc:
                raise _failed(f"The decision model returned an invalid response: {exc}") from None
        except EvaluationException as exc:
            if exc.properties is None:
                exc.properties = properties
            raise

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

    async def _await_request(self, content: bytes, deadline: float) -> Any:
        if self._cancelled():
            raise _failed("The decision model request was cancelled.", ErrorBlame.USER_ERROR)
        if self._cancellation_requested is None:
            return await self._post(content, deadline=deadline)
        task = asyncio.create_task(self._post(content, deadline=deadline))
        try:
            while not task.done():
                if self._cancelled():
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

    async def _post(self, content: bytes, *, deadline: float) -> Any:
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
            diagnostic = f" ({code})" if isinstance(code, str) and code in _DECISION_SAFE_ERROR_CODES else ""
            error = _failed(f"The decision model returned HTTP {status}{diagnostic}.", blame)
            error.properties = self._response_properties(payload)
            raise error
        return payload

    def _response_properties(self, payload: Any) -> Dict[str, Any]:
        """Retain only independently known final-response usage, never raw answers or retry totals."""
        properties: Dict[str, Any] = {"decision_model": {"deployment": self._deployment}}
        usage = payload.get("usage") if isinstance(payload, dict) else None
        usage = usage if isinstance(usage, dict) else {}
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

    @staticmethod
    def _validate_response(payload: Any, questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        # Only the response's structure is checked here; answer values are validated by the evaluator after it
        # has read the status answer, so a skipped evaluation never depends on an unusable score.
        if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
            raise ValueError("answers are missing.")
        answers = payload["answers"]
        if set(answers) != set(questions):
            raise ValueError("answer identifiers do not match the questions.")
        for question_id, question in questions.items():
            answer = answers[question_id]
            question_type = question.get("type")
            if not isinstance(answer, dict) or answer.get("type") != question_type:
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
        }
