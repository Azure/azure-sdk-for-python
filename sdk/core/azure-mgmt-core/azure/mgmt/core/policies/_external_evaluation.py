# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Experimental, opt-in orchestration for ARM external evaluation."""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Union
from urllib.parse import urlsplit

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import (
    HttpRequest as LegacyHttpRequest,
    HttpResponse as LegacyHttpResponse,
)
from azure.core.rest import HttpRequest, HttpResponse

from ..exceptions import ARMErrorFormat

_LOGGER = logging.getLogger(__name__)
_HEADER = "x-ms-policy-external-evaluations"
_METHODS = frozenset(("PUT", "PATCH", "POST", "DELETE"))
_SUBSCRIPTION = re.compile(
    r"^/subscriptions/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:/|$)",
    re.IGNORECASE,
)
HTTPRequestType = Union[LegacyHttpRequest, HttpRequest]
HTTPResponseType = Union[LegacyHttpResponse, HttpResponse]


@dataclass(frozen=True)
class PolicyTokenRequestContext:
    """Immutable operation details passed to a policy-token provider.

    :param str uri: The complete URI of the guarded operation.
    :param str http_method: The HTTP method of the guarded operation.
    :param str subscription_id: The subscription identified by the operation URI.
    :param content: The exact UTF-8 JSON body, or None for a bodyless operation.
    :type content: bytes or None
    """

    uri: str
    http_method: str
    subscription_id: str
    content: Optional[bytes]

    def get_request_body(self) -> bytes:
        """Build the acquisition envelope without reserializing the operation body.

        :return: A JSON body suitable for ``policy_tokens.acquire(BytesIO(body))``.
        :rtype: bytes
        """
        operation = json.dumps({"uri": self.uri, "httpMethod": self.http_method}).encode("utf-8")
        if self.content:
            # Embed the original JSON value, not a parsed model or a JSON string.
            json.loads(self.content)
            operation = operation[:-1] + b',"content":' + self.content + b"}"
        return b'{"operation":' + operation + b"}"


def _eligible(request: HTTPRequestType) -> bool:
    url = urlsplit(request.url)
    return (
        request.method.upper() in _METHODS
        and _HEADER not in request.headers
        and url.scheme.lower() == "https"
        and url.hostname is not None
        and url.username is None
        and url.password is None
        and _SUBSCRIPTION.match(url.path) is not None
        and not url.path.lower().rstrip("/").endswith("/acquirepolicytoken")
    )


def _missing_token_details(text: str) -> list[Mapping[str, Any]]:
    try:
        payload = json.loads(text)
    except (ValueError, UnicodeError):
        _LOGGER.warning("Unable to parse the ARM policy response; external evaluation was not attempted.")
        return []
    if not isinstance(payload, Mapping):
        return []
    error = payload.get("error")
    if not isinstance(error, Mapping) or error.get("code") != "RequestDisallowedByPolicy":
        return []

    def collect(node: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        hints = []
        additional_info = node.get("additionalInfo", [])
        if isinstance(additional_info, list):
            for entry in additional_info:
                if not isinstance(entry, Mapping):
                    continue
                info = entry.get("info")
                evaluation = info.get("evaluationDetails") if isinstance(info, Mapping) else None
                hint = evaluation.get("missingPolicyTokenDetails") if isinstance(evaluation, Mapping) else None
                if isinstance(hint, Mapping):
                    hints.append(hint)
        details = node.get("details", [])
        if isinstance(details, list):
            for detail in details:
                if isinstance(detail, Mapping):
                    hints.extend(collect(detail))
        return hints

    return collect(error)


def _denied(response: Any, message: str) -> HttpResponseError:
    def error_format(payload: Mapping[str, Any]) -> ARMErrorFormat:
        error = ARMErrorFormat(payload)
        error.message = "{}\n{}".format(error.message or "", message)
        return error

    return HttpResponseError(message=message, response=response, error_format=error_format)


def _acquisition_context(
    request: HTTPRequestType, response: Any, hints: list[Mapping[str, Any]]
) -> PolicyTokenRequestContext:
    if any(hint.get("isChangeReferenceRequired", False) is not False for hint in hints):
        raise _denied(
            response,
            "External evaluation requires a change reference. Automatic ChangeSafety integration is not supported.",
        )
    body = request.content if isinstance(request, HttpRequest) else request.body
    if isinstance(body, str):
        body = body.encode("utf-8")
    if body is not None and not isinstance(body, bytes):
        raise _denied(
            response,
            "External evaluation supports only in-memory JSON bodies and bodyless operations.",
        )
    if body:
        content_type = request.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json" and not content_type.endswith("+json"):
            raise _denied(
                response,
                "External evaluation requires a JSON content type for requests with a body.",
            )
        try:
            json.loads(body)
        except (ValueError, UnicodeError) as error:
            raise _denied(response, "External evaluation requires a valid UTF-8 JSON body.") from error
        try:
            body.decode("utf-8")
        except UnicodeError as error:
            raise _denied(response, "External evaluation requires a valid UTF-8 JSON body.") from error
    match = _SUBSCRIPTION.match(urlsplit(request.url).path)
    if match is None:
        raise _denied(response, "External evaluation could not identify the subscription.")
    return PolicyTokenRequestContext(request.url, request.method, match.group(1), body)


def _get_token(result: Mapping[str, Any], response: Any) -> str:
    if not isinstance(result, Mapping) or result.get("result") != "Succeeded":
        raise _denied(
            response,
            "Policy-token acquisition failed; the original operation was not replayed.",
        )
    results = result.get("results")
    if (
        not isinstance(results, list)
        or not results
        or any(
            not isinstance(item, Mapping)
            or item.get("result", "Succeeded") != "Succeeded"
            or item.get("policyAction") not in ("Allow", "Audit")
            for item in results
        )
    ):
        raise _denied(
            response,
            "External evaluation did not allow the operation; inspect the original policy details.",
        )
    token = result.get("token")
    if not isinstance(token, str) or not token.strip() or "\r" in token or "\n" in token:
        raise _denied(response, "Policy-token acquisition did not return a valid token.")
    return token


def _replay_request(request: HTTPRequestType, context: PolicyTokenRequestContext, token: str) -> HTTPRequestType:
    headers = dict(request.headers)
    headers[_HEADER] = token
    if context.content is not None:
        headers["Content-Length"] = str(len(context.content))
    if isinstance(request, HttpRequest):
        return HttpRequest(context.http_method, context.uri, headers=headers, content=context.content)
    return LegacyHttpRequest(context.http_method, context.uri, headers=headers, data=context.content)


class ExternalEvaluationPolicy(HTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Opt in to subscription-level ARM external evaluation.

    Install before the retry and authentication policies, using ``per_call_policies``.
    The provider must use a separate client without this policy and protect the
    acquisition response from body logging. Only replayable, in-memory JSON and
    bodyless write requests are supported. ChangeSafety is not automated.

    :param policy_token_provider: Callback returning the acquisition response, including
        ``result``, ``results``, and the opaque ``token``. The callback receives an
        immutable request context.
    :type policy_token_provider: callable[
        [~azure.mgmt.core.policies.PolicyTokenRequestContext], Mapping[str, Any]]
    """

    def __init__(
        self,
        policy_token_provider: Callable[[PolicyTokenRequestContext], Mapping[str, Any]],
    ) -> None:
        if not callable(policy_token_provider):
            raise TypeError("policy_token_provider must be callable.")
        self._provider = policy_token_provider

    def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]:
        """Acquire and replay once when ARM reports a missing policy token.

        :param request: The pipeline request.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The original response or the response from the token-bound replay.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises ~azure.core.exceptions.HttpResponseError: If acquisition or evaluation fails.
        """
        initially_eligible = _eligible(request.http_request)
        original_origin = urlsplit(request.http_request.url).netloc.lower()
        response = self.next.send(request)
        http_request = request.http_request
        if (
            not initially_eligible
            or not _eligible(http_request)
            or response.http_response.status_code != 403
            or urlsplit(http_request.url).netloc.lower() != original_origin
        ):
            return response
        if isinstance(response.http_response, HttpResponse):
            response.http_response.read()
        hints = _missing_token_details(response.http_response.text())
        if not hints:
            return response
        context = _acquisition_context(http_request, response.http_response, hints)
        try:
            result = self._provider(context)
        except AzureError as error:
            raise _denied(
                response.http_response,
                "Policy-token acquisition failed; see the chained exception.",
            ) from error
        token = _get_token(result, response.http_response)
        request.http_request = _replay_request(http_request, context, token)
        # Do not forward the token through a redirect or expose it in debug body/header logs.
        request.context.options.update(permit_redirects=False, logging_enable=False)
        return self.next.send(request)
