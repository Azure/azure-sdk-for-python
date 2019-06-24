# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import time

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

import httpretty

from azure.identity import ManagedIdentityCredential
from azure.identity.constants import Endpoints, EnvironmentVariables


@httpretty.activate
def test_cloud_shell():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.POST, url, body=token_json, content_type="application/json")

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: url}):
        token = ManagedIdentityCredential().get_token("scope")
        assert token.token == access_token
        last_request = httpretty.last_request()
        assert last_request.headers["Metadata"] == "true"
        assert b"resource=scope" in last_request.body


@httpretty.activate
def test_cloud_shell_user_assigned_identity():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.POST, url, body=token_json, content_type="application/json")

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: url}):
        token = ManagedIdentityCredential(client_id="some-guid").get_token("scope")
        assert token.token == access_token
        assert httpretty.last_request().headers["Metadata"] == "true"
        assert b"client_id=some-guid" in httpretty.last_request().body
        assert b"resource=scope" in httpretty.last_request().body


@httpretty.activate
def test_app_service():
    """App Service environment: MSI_ENDPOINT, MSI_SECRET set"""

    expected_secret = "expected-secret"

    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.GET, url, body=token_json, content_type="application/json")

    with mock.patch(
        "os.environ", {EnvironmentVariables.MSI_ENDPOINT: url, EnvironmentVariables.MSI_SECRET: expected_secret}
    ):
        token = ManagedIdentityCredential().get_token("scope")
        assert token.token == access_token
        assert httpretty.last_request().headers["secret"] == expected_secret
        assert len(httpretty.httpretty.latest_requests) == 1


@httpretty.activate
def test_app_service_user_assigned_identity():
    """App Service environment: MSI_ENDPOINT, MSI_SECRET set"""

    expected_secret = "expected-secret"
    client_id = "some-guid"
    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.GET, url, body=token_json, content_type="application/json")

    with mock.patch(
        "os.environ", {EnvironmentVariables.MSI_ENDPOINT: url, EnvironmentVariables.MSI_SECRET: expected_secret}
    ):
        token = ManagedIdentityCredential(client_id=client_id).get_token("scope")
        assert token.token == access_token
        assert len(httpretty.httpretty.latest_requests) == 1
        last_request = httpretty.last_request()
        assert last_request.headers["secret"] == expected_secret
        assert last_request.querystring.get("client_id") == [client_id]  # pylint:disable=no-member


@httpretty.activate
def test_imds():
    access_token = "AccessToken"
    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    scope = "scope"

    class reqs:
        count = 0

    def request_callback(request, uri, response_headers):
        reqs.count += 1
        if reqs.count == 1:
            # credential is probing to determine endpoint availability
            return 400, response_headers, json.dumps({})
        assert request.headers["Metadata"] == "true"
        assert request.querystring.get("resource") == [scope]
        return 200, response_headers, token_json

    httpretty.register_uri(httpretty.GET, Endpoints.IMDS, body=request_callback, content_type="application/json")

    token = ManagedIdentityCredential().get_token("scope")
    assert token.token == access_token


@httpretty.activate
def test_imds_user_assigned_identity():
    access_token = "AccessToken"
    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    scope = "scope"
    client_id = "client-id"

    class reqs:
        count = 0

    def request_callback(request, uri, response_headers):
        reqs.count += 1
        if reqs.count == 1:
            # credential is probing to determine endpoint availability
            return 400, response_headers, json.dumps({})
        assert request.headers["Metadata"] == "true"
        assert request.querystring.get("client_id") == [client_id]
        assert request.querystring.get("resource") == [scope]
        return 200, response_headers, token_json

    httpretty.register_uri(httpretty.GET, Endpoints.IMDS, body=request_callback, content_type="application/json")

    token = ManagedIdentityCredential(client_id=client_id).get_token(scope)
    assert token.token == access_token
    assert len(httpretty.httpretty.latest_requests) == 2
