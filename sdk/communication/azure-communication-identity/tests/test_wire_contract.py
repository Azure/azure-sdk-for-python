# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Wire-contract tests for CommunicationIdentityClient.

These assert what the client actually puts on the wire, rather than what the
convenience layer returns. They exist because the move from AutoRest to the
TypeSpec DPG emitter changed three things that are invisible to an API-surface
check and are not covered by the recorded tests:

1. ``expiresInMinutes`` must be omitted when the caller supplies no expiry.
   msrest dropped ``None`` fields during serialization; the generated code
   forwards the request body as-is, so without a fix an explicit ``null``
   reaches a property the service constrains to [60, 1440].

2. ``AccessToken.expires_on`` must remain the raw service string. The TypeSpec
   model declares ``expiresOn: utcDateTime``, so attribute access on the
   generated model returns a ``datetime``; every published version of this SDK
   exposed the string.

3. The default api-version must be the one the package claims to target.

Requests are captured at the transport, which is the last pipeline stage before
the network, so these are wire observations rather than serializer return
values.
"""

import json
from datetime import timedelta

import pytest
from azure.core.pipeline.transport import HttpTransport

from azure.communication.identity import (
    CommunicationIdentityClient,
    CommunicationTokenScope,
)
from azure.communication.identity._api_versions import DEFAULT_VERSION
from azure.communication.identity._shared.models import CommunicationUserIdentifier

WIRE_EXPIRY = "2026-09-23T12:00:00.1234567Z"
EXPECTED_API_VERSION = "2026-09-23"
FAKE_ENDPOINT = "https://sanitized.communication.azure.com"
FAKE_KEY = "a2V5" * 8


class _FakeResponse:
    def __init__(self, request, status_code, body):
        self.request = request
        self.status_code = status_code
        self._body = json.dumps(body).encode() if body is not None else b""
        self.headers = {"content-type": "application/json"}
        self.reason = "OK"
        self.content_type = "application/json"
        self.is_closed = True
        self.is_stream_consumed = True

    @property
    def content(self):
        return self._body

    def text(self, encoding=None):
        return self._body.decode()

    def json(self):
        return json.loads(self._body)

    def read(self):
        return self._body

    def close(self):
        pass

    def raise_for_status(self):
        pass


class _CapturingTransport(HttpTransport):
    """Records each outgoing request and replies with a canned response."""

    def __init__(self):
        self.requests = []

    def send(self, request, **kwargs):
        self.requests.append(request)
        token = {"token": "jwt.tok.sig", "expiresOn": WIRE_EXPIRY}
        path = request.url.split("?")[0]
        if path.endswith("/identities"):
            return _FakeResponse(request, 201, {"identity": {"id": "8:acs:u"}, "accessToken": token})
        if path.endswith(":issueAccessToken") or path.endswith("teamsUser/:exchangeAccessToken"):
            return _FakeResponse(request, 200, token)
        return _FakeResponse(request, 204, None)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@pytest.fixture
def transport():
    return _CapturingTransport()


@pytest.fixture
def client(transport):
    return CommunicationIdentityClient(FAKE_ENDPOINT, FAKE_KEY, transport=transport)


def _sent_body(transport):
    return json.loads(transport.requests[-1].content)


class TestRequestBody:
    """expiresInMinutes must be absent unless the caller asked for an expiry."""

    def test_create_user_and_token_omits_expiry_when_not_requested(self, client, transport):
        client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        body = _sent_body(transport)
        assert "expiresInMinutes" not in body
        assert body["createTokenWithScopes"] == ["chat"]

    def test_create_user_and_token_sends_expiry_when_requested(self, client, transport):
        client.create_user_and_token(
            scopes=[CommunicationTokenScope.CHAT],
            token_expires_in=timedelta(hours=2),
        )
        assert _sent_body(transport)["expiresInMinutes"] == 120

    def test_get_token_omits_expiry_when_not_requested(self, client, transport):
        client.get_token(CommunicationUserIdentifier("8:acs:u"), scopes=[CommunicationTokenScope.VOIP])
        body = _sent_body(transport)
        assert "expiresInMinutes" not in body
        assert body["scopes"] == ["voip"]

    def test_get_token_sends_expiry_when_requested(self, client, transport):
        client.get_token(
            CommunicationUserIdentifier("8:acs:u"),
            scopes=[CommunicationTokenScope.VOIP],
            token_expires_in=timedelta(hours=3),
        )
        assert _sent_body(transport)["expiresInMinutes"] == 180

    def test_none_scopes_are_omitted_not_sent_as_null(self, client, transport):
        """A None scope list must be dropped, as msrest dropped it.

        Passing None for a required argument is a caller error, but it has to fail the way it
        always failed. The AutoRest client sent {} because msrest omitted None fields; sending
        {"scopes": null} instead is a different request for a proxy, gateway or log to observe.
        This does not assert an exception: the previous client did not raise here either.
        """
        try:
            client.get_token(CommunicationUserIdentifier("8:acs:u"), None)
        except Exception:  # pylint: disable=broad-except
            pass
        assert _sent_body(transport) == {}

    def test_none_create_scopes_are_omitted_not_sent_as_null(self, client, transport):
        try:
            client.create_user_and_token(None)
        except Exception:  # pylint: disable=broad-except
            pass
        assert _sent_body(transport) == {}

    def test_empty_scope_list_is_still_sent(self, client, transport):
        """An empty list is a value, not an absence, and must survive."""
        try:
            client.get_token(CommunicationUserIdentifier("8:acs:u"), [])
        except Exception:  # pylint: disable=broad-except
            pass
        assert _sent_body(transport) == {"scopes": []}


class TestAccessTokenExpiry:
    """expires_on must be the untouched service string, not a deserialized datetime."""

    def test_create_user_and_token_expiry_is_raw_string(self, client):
        _, token = client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        assert isinstance(token.expires_on, str)
        assert token.expires_on == WIRE_EXPIRY

    def test_get_token_expiry_is_raw_string(self, client):
        token = client.get_token(CommunicationUserIdentifier("8:acs:u"), scopes=[CommunicationTokenScope.CHAT])
        assert isinstance(token.expires_on, str)
        assert token.expires_on == WIRE_EXPIRY

    def test_get_token_for_teams_user_expiry_is_raw_string(self, client):
        token = client.get_token_for_teams_user("aad-token", "client-id", "user-object-id")
        assert isinstance(token.expires_on, str)
        assert token.expires_on == WIRE_EXPIRY


class TestRequestHeaders:
    """Request headers must match what the AutoRest-generated client sent.

    The TypeSpec DPG emitter drops three headers the previous client sent:
    ``Content-Type`` on the bodyless ``create_user`` POST, and ``Accept`` on
    ``revoke_tokens`` and ``delete_user`` (both typed as 204-no-content, for
    which the emitter produces no ``Accept``).

    The service is indifferent to these -- measured against a live resource --
    but a proxy, gateway or request log keying on headers would observe the
    change, so they are restored in the convenience layer.

    Expected values are literals rather than references to the constants that
    produce them: asserting against ``_ACCEPT_JSON`` would compare the wire to
    the same value that set it and would pass even if both were wrong.
    """

    def test_create_user_sends_content_type(self, client, transport):
        client.create_user()
        assert transport.requests[-1].headers["Content-Type"] == "application/json"

    def test_create_user_sends_no_body_despite_content_type(self, client, transport):
        """Content-Type must not cause a body to be sent -- AutoRest sent none."""
        client.create_user()
        assert transport.requests[-1].content is None

    def test_revoke_tokens_sends_accept(self, client, transport):
        client.revoke_tokens(CommunicationUserIdentifier("8:acs:u"))
        assert transport.requests[-1].headers["Accept"] == "application/json"

    def test_delete_user_sends_accept(self, client, transport):
        client.delete_user(CommunicationUserIdentifier("8:acs:u"))
        assert transport.requests[-1].headers["Accept"] == "application/json"

    def test_body_bearing_operations_still_send_both_headers(self, client, transport):
        client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        headers = transport.requests[-1].headers
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_caller_supplied_content_type_is_not_overridden(self, client, transport):
        """The policy must defer to a Content-Type already on the request."""
        client.create_user(headers={"Content-Type": "application/custom"})
        assert transport.requests[-1].headers["Content-Type"] == "application/custom"


class TestApiVersion:
    """Every request must carry the api-version the package targets.

    The expected version is asserted as a literal rather than by reading
    ``DEFAULT_VERSION``. Comparing the wire against the same constant that
    produced it is self-referential and cannot detect a wrong default -- that
    weakness was found by mutation testing, where changing ``DEFAULT_VERSION``
    left the loop below passing.
    """

    def test_default_api_version_is_sent_on_every_operation(self, client, transport):
        user = CommunicationUserIdentifier("8:acs:u")
        client.create_user()
        client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        client.get_token_for_teams_user("aad-token", "client-id", "user-object-id")
        client.revoke_tokens(user)
        client.delete_user(user)

        assert len(transport.requests) == 6
        for request in transport.requests:
            assert f"api-version={EXPECTED_API_VERSION}" in request.url

    def test_default_api_version_matches_shipped_value(self):
        assert DEFAULT_VERSION.value == EXPECTED_API_VERSION
