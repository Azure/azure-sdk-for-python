# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import timedelta
from typing import Any, Dict, List, Optional, Union
from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import SansIOHTTPPolicy

# Headers the AutoRest-generated client sent that the TypeSpec DPG emitter does not.
#
# Restoring them keeps the request black-box identical to the previously published SDK. The
# service itself is indifferent -- measured against a live resource, `Accept` makes no
# difference to either the success or the error path -- but a proxy, gateway or request log
# keying on headers would observe the change, so the difference is customer-visible even
# though the service ignores it.
#
# Why the emitter drops them:
#   - `delete` and `revoke_access_tokens` return 204 with no response body, so the emitter
#     emits no `Accept` header for them at all.
#   - `create` declares `content_type` only as a body-parameter keyword, so with no body
#     passed it is never applied.
#
# These are request headers only. Sending `Content-Type` does not cause a body to be sent;
# the body remains absent for `create_user`, as it was under AutoRest.
_ACCEPT_JSON = {"Accept": "application/json"}
_CONTENT_TYPE_JSON = {"Content-Type": "application/json"}


def to_access_token(access_token: Any) -> AccessToken:
    """Build an AccessToken from a generated CommunicationIdentityAccessToken.

    ``expiresOn`` is read **by key**, not via the ``.expires_on`` attribute. Do not
    "simplify" this to attribute access: the two are not equivalent.

    The TypeSpec model declares ``expiresOn: utcDateTime``, so the generated model types it
    as ``datetime.datetime`` and attribute access returns a deserialized ``datetime``. Every
    previously published version of this SDK exposed the raw service string, so returning a
    ``datetime`` would be a breaking change for callers. Item access on the generated model
    returns the untouched wire value, which keeps the public surface unchanged.

    This is a re-occurrence, not a new concern. The AutoRest configuration formerly at
    ``swagger/SWAGGER.md`` carried a directive deleting ``format: date-time`` from this same
    property, added because a generator upgrade had already turned it from string into
    ``datetime`` once before. That directive acted on the swagger document and does not carry
    over to TypeSpec, so this function is now the only thing preventing the same break.

    ``.isoformat()`` is **not** an adequate substitute: it reformats the value (``Z`` becomes
    ``+00:00``) and silently truncates the service's 7-digit fractional seconds to 6.

    :param access_token: A generated CommunicationIdentityAccessToken instance.
    :type access_token: ~azure.communication.identity._generated.models.CommunicationIdentityAccessToken
    :return: The access token and its expiry, as returned by the service.
    :rtype: ~azure.core.credentials.AccessToken
    """
    return AccessToken(access_token["token"], access_token["expiresOn"])


def build_token_request_body(
    scopes_key: str,
    scopes: List[Union[str, Any]],
    token_expires_in: Optional[timedelta],
) -> Dict[str, Any]:
    """Build a token request body, omitting fields the caller did not supply.

    The previous msrest-based layer dropped ``None`` fields during serialization, whereas the
    generated code forwards the request body as-is. Both ``scopes`` and ``expiresInMinutes``
    are therefore omitted when unset, so the request stays byte-identical to the previously
    published SDK.

    ``expiresInMinutes`` matters because the service constrains it to [60, 1440] and an
    explicit ``null`` is not a valid value. ``scopes`` is omitted for the same reason the old
    layer omitted it -- passing ``None`` for a required argument is a caller error either way,
    but it must fail the way it always failed, with the same request on the wire.

    Note this restores prior behaviour rather than adding validation: the AutoRest client did
    not raise on a ``None`` scope list, and neither does this. The request is still sent and
    the service still rejects it.

    :param scopes_key: Name of the scopes property expected by the service.
    :type scopes_key: str
    :param scopes: List of scopes to be added to the token.
    :type scopes: list[str or ~azure.communication.identity.CommunicationTokenScope]
    :param token_expires_in: Optional custom validity period of the token.
    :type token_expires_in: ~datetime.timedelta or None
    :return: The request body to send to the service.
    :rtype: dict[str, any]
    """
    request_body: Dict[str, Any] = {}
    if scopes is not None:
        request_body[scopes_key] = scopes
    expires_in_minutes = convert_timedelta_to_mins(token_expires_in)
    if expires_in_minutes is not None:
        request_body["expiresInMinutes"] = expires_in_minutes
    return request_body


def extract_create_content_type(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve a caller-supplied ``Content-Type`` across the generated create operation.

    The operation discards it when no body is present, so it is moved into the
    request context for :class:`BodylessCreateContentTypePolicy` to reapply.

    :param kwargs: Keyword arguments destined for the create operation.
    :type kwargs: dict[str, any]
    :return: The keyword arguments, with any Content-Type moved to the context.
    :rtype: dict[str, any]
    """
    headers = kwargs.get("headers") or {}
    override = kwargs.pop("content_type", None)
    for name in list(headers):
        if name.lower() == "content-type":
            override = headers.pop(name)
    if override:
        kwargs[BodylessCreateContentTypePolicy.CONTEXT_KEY] = override
    return kwargs


def merge_headers(kwargs: Dict[str, Any], defaults: Dict[str, str]) -> Dict[str, Any]:
    """Add default request headers without overriding any the caller supplied.

    :param kwargs: Keyword arguments destined for a generated operation.
    :type kwargs: dict[str, any]
    :param defaults: Headers to apply when the caller has not set them.
    :type defaults: dict[str, str]
    :return: The keyword arguments, with a merged ``headers`` entry.
    :rtype: dict[str, any]
    """
    headers = dict(kwargs.pop("headers", None) or {})
    existing = {name.lower() for name in headers}
    for name, value in defaults.items():
        if name.lower() not in existing:
            headers[name] = value
    kwargs["headers"] = headers
    return kwargs


class BodylessCreateContentTypePolicy(SansIOHTTPPolicy):
    """Restores ``Content-Type`` on the bodyless identity-create request.

    The generated ``create`` operation discards ``content_type`` whenever no body
    is present -- twice, via ``content_type if body else None`` and again via
    ``content_type or "application/json" if body else None`` -- so no argument
    passed to the operation can survive. A policy is therefore the only way to
    restore the header without editing generated code.

    The same discard also drops a caller-supplied ``Content-Type``, which the
    AutoRest client honoured. ``CommunicationIdentityClient.create_user``
    consequently stashes any caller value on the request context under
    ``_acs_create_content_type`` and this policy reapplies it, so an explicit
    override still reaches the wire.

    The match is deliberately narrow: a POST to the identities collection with no
    body. ``create_user_and_token`` sends a body and so already carries the header
    from the generated code, and is left untouched.
    """

    CONTEXT_KEY = "_acs_create_content_type"

    def on_request(self, request) -> None:
        http_request = request.http_request
        if http_request.method != "POST":
            return
        if not http_request.url.split("?")[0].endswith("/identities"):
            return
        # The generated operation drops content_type whenever the body is falsy, which covers
        # both no body at all and an empty JSON object. Both must be repaired, so the test is
        # "did the operation fail to set a JSON content type", not "is there a body" -- an
        # empty dict serializes to the string "{}", which is truthy and would be missed.
        if http_request.headers.get("Content-Type", "").startswith("application/json"):
            return
        override = request.context.options.pop(self.CONTEXT_KEY, None)
        http_request.headers["Content-Type"] = override or "application/json"


def convert_timedelta_to_mins(
    duration: Optional[timedelta],
) -> Optional[int]:
    """
    Returns the total number of minutes contained in the duration.
    :param duration: Time duration
    :type duration: ~datetime.timedelta
    :rtype: int
    """
    return None if duration is None else int(duration.total_seconds() / 60)
