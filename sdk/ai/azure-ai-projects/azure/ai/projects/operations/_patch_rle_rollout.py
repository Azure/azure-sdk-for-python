# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared request/response plumbing for the RLE Execute Rollout operation.

The sync and async operation groups differ only in how they await the pipeline and the
credential, so everything else -- URL construction, body shaping, error surfacing -- lives here
and is used by both. Keeping it in one place is what stops the two surfaces from drifting into
sending subtly different requests.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Mapping, Optional
from urllib.parse import quote

from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest

from ..models import RLERolloutPolicy, RLERolloutRequest, RLERolloutResult, RLESamplingOptions

# The Foundry data plane gates ``:executeRollout`` on this preview api-version. It is
# deliberately not ``config.api_version`` (``v1``), which the instance-level RLE routes use:
# the two are separate contracts on the same endpoint, and pinning the rollout route to the
# version it was shipped under keeps a client-wide api_version override from silently moving it.
EXECUTE_ROLLOUT_API_VERSION = "2025-11-15-preview"

# The classic AzureML forwarded-user-token header. RLE requires it in addition to
# ``Authorization`` and forwards it unchanged to Capture Proxy, which presents it to Loom as a
# raw bearer when opening the rollout's sampling session. Both consumers require the
# ``https://ai.azure.com`` audience, which is the client's own credential scope, so the SDK
# acquires it rather than making the caller plumb a second token.
FORWARDED_TOKEN_HEADER = "aml-user-token"

_ROLLOUT_PATH_TEMPLATE = "/rl_environments/{name}/versions/{version}:executeRollout"


class RLERolloutError(HttpResponseError):
    """An Execute Rollout call that the service refused or could not complete.

    RLE answers failures with a flat ``{"code", "message"}`` body rather than the nested
    ``error`` envelope azure-core expects, so the code and message are lifted onto the exception
    here instead of being left buried in an unparsed response.

    :ivar code: Stable machine-readable failure code, such as ``RolloutDependencyFailed``.
    :vartype code: str or None
    :ivar rollout_id: The rollout this failure belongs to, echoed for log correlation.
    :vartype rollout_id: str or None
    """

    def __init__(
        self,
        response: Any,
        *,
        code: Optional[str] = None,
        message: Optional[str] = None,
        rollout_id: Optional[str] = None,
    ) -> None:
        self.code = code
        self.rollout_id = rollout_id
        detail = message or "the RLE service did not complete the rollout"
        prefix = f"{code}: " if code else ""
        suffix = f" (rollout_id={rollout_id})" if rollout_id else ""
        composed = f"{prefix}{detail}{suffix}"
        super().__init__(message=composed, response=response)
        # HttpResponseError replaces the supplied message whenever it manages to parse the body
        # as OData, which RLE's flat {code, message} does satisfy. That would drop the rollout id
        # -- the one value that leads to the logged cause -- so the composed message is restored
        # here. ``args`` carries it too, because Exception.__str__ reads args rather than
        # ``message``. The parsed ``error`` is left intact for callers that read it.
        self.message = composed
        self.args = (composed,)


def build_rollout_request(
    *,
    environment_name: str,
    environment_version: str,
    body: RLERolloutRequest,
    forwarded_token: str,
    api_version: str = EXECUTE_ROLLOUT_API_VERSION,
) -> HttpRequest:
    """Shape one ``:executeRollout`` request, relative to the client's project endpoint.

    :keyword environment_name: Published environment name.
    :paramtype environment_name: str
    :keyword environment_version: Exact version to run. Never resolved to "latest": a rollout is
     pinned so the trajectory it returns names the code that produced it.
    :paramtype environment_version: str
    :keyword body: The rollout request.
    :paramtype body: ~azure.ai.projects.models.RLERolloutRequest
    :keyword forwarded_token: Bearer token forwarded to Capture Proxy for Loom sampling.
    :paramtype forwarded_token: str
    :keyword api_version: Data-plane api-version for this route.
    :paramtype api_version: str
    :return: The prepared request.
    :rtype: ~azure.core.rest.HttpRequest
    """
    url = _ROLLOUT_PATH_TEMPLATE.format(
        name=quote(environment_name, safe=""),
        version=quote(environment_version, safe=""),
    )
    return HttpRequest(
        method="POST",
        url=url,
        params={"api-version": api_version},
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            FORWARDED_TOKEN_HEADER: forwarded_token,
        },
        content=json.dumps(body.as_dict()),
    )


def build_rollout_body(
    *,
    task: Any,
    policy: RLERolloutPolicy,
    sampling: Optional[RLESamplingOptions] = None,
    rollout_id: Optional[str] = None,
) -> RLERolloutRequest:
    """Assemble a rollout request, generating an id when the caller did not supply one.

    The generated id is a bare-hex UUID, the form RLE reserves per project. A caller that wants
    to correlate a rollout with its own records should pass ``rollout_id`` instead, since the
    service returns whatever it was given unchanged.

    :keyword task: Opaque task record forwarded to the environment's reset.
    :paramtype task: any
    :keyword policy: Where this rollout's weights come from.
    :paramtype policy: ~azure.ai.projects.models.RLERolloutPolicy
    :keyword sampling: How completions are sampled and rendered.
    :paramtype sampling: ~azure.ai.projects.models.RLESamplingOptions or None
    :keyword rollout_id: Caller-supplied identifier. Generated when omitted.
    :paramtype rollout_id: str or None
    :return: The assembled request.
    :rtype: ~azure.ai.projects.models.RLERolloutRequest
    """
    if task is None:
        raise ValueError("task is required: it is the record the environment resets on")
    if policy is None:
        raise ValueError("policy is required: a rollout must name where its weights come from")
    return RLERolloutRequest(
        rollout_id=rollout_id or uuid.uuid4().hex,
        task=task,
        policy=policy,
        sampling=sampling,
    )


def deserialize_rollout_response(response: Any, rollout_id: str) -> RLERolloutResult:
    """Turn a completed pipeline response into a result, or raise with the service's own code.

    :param response: The HTTP response.
    :type response: any
    :param rollout_id: The requested rollout id, used to correlate a failure.
    :type rollout_id: str
    :return: The rollout result.
    :rtype: ~azure.ai.projects.models.RLERolloutResult
    :raises ~azure.ai.projects.operations.RLERolloutError: If the service did not return 200.
    """
    if response.status_code != 200:
        code, message = _read_error(response)
        raise RLERolloutError(response, code=code, message=message, rollout_id=rollout_id)
    return RLERolloutResult(response.json())


def _read_error(response: Any) -> "tuple[Optional[str], Optional[str]]":
    """Extract RLE's flat ``{code, message}``, tolerating anything else.

    A failure to parse an error must never replace the error: if the body is not the shape we
    expect -- a gateway's HTML, a truncated response -- the status code still reaches the caller
    through the raised exception, which is more than a parse error would leave them with.
    """
    try:
        body = response.json()
    except Exception:  # pylint: disable=broad-except
        return None, None
    if not isinstance(body, Mapping):
        return None, None
    code = body.get("code")
    message = body.get("message")
    # Also accept the nested envelope, in case a gateway ahead of RLE answers instead of RLE.
    error = body.get("error")
    if isinstance(error, Mapping):
        code = code or error.get("code")
        message = message or error.get("message")
    return (
        code if isinstance(code, str) else None,
        message if isinstance(message, str) else None,
    )
