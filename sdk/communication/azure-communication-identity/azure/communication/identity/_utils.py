# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import timedelta
from typing import Any, Dict, List, Optional, Union
from azure.core.credentials import AccessToken


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
    """Build a token request body, omitting the expiry when it was not requested.

    ``expiresInMinutes`` is only included when the caller supplied a value. The previous
    msrest-based layer dropped ``None`` fields during serialization, whereas the generated
    code now forwards the request body as-is, which would put an explicit ``null`` on the
    wire for a property the service constrains to [60, 1440].

    :param scopes_key: Name of the scopes property expected by the service.
    :type scopes_key: str
    :param scopes: List of scopes to be added to the token.
    :type scopes: list[str or ~azure.communication.identity.CommunicationTokenScope]
    :param token_expires_in: Optional custom validity period of the token.
    :type token_expires_in: ~datetime.timedelta or None
    :return: The request body to send to the service.
    :rtype: dict[str, any]
    """
    request_body: Dict[str, Any] = {scopes_key: scopes}
    expires_in_minutes = convert_timedelta_to_mins(token_expires_in)
    if expires_in_minutes is not None:
        request_body["expiresInMinutes"] = expires_in_minutes
    return request_body


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
