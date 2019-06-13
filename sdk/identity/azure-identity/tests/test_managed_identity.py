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
    import mock

import httpretty

from azure.identity import ManagedIdentityCredential
from azure.identity.constants import Endpoints, MSI_ENDPOINT, MSI_SECRET


@httpretty.activate
def test_cloud_shell():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.POST, url, body=token_json, content_type="application/json")

    with mock.patch("os.environ", {MSI_ENDPOINT: url}):
        token = ManagedIdentityCredential().get_token("scope")
        assert token == access_token
        assert httpretty.last_request().headers["Metadata"] == "true"
        assert b"resource=scope" in httpretty.last_request().body

        # try user assigned identities
        token = ManagedIdentityCredential(user_assigned_identity={"client_id": "some-guid"}).get_token("scope")
        assert token == access_token
        assert httpretty.last_request().headers["Metadata"] == "true"
        assert b"client_id=some-guid" in httpretty.last_request().body
        assert b"resource=scope" in httpretty.last_request().body

        ManagedIdentityCredential(user_assigned_identity={"object_id": "some-guid"}).get_token("scope")
        assert b"object_id=some-guid" in httpretty.last_request().body

        ManagedIdentityCredential(user_assigned_identity={"msi_res_id": "some-guid"}).get_token("scope")
        assert b"msi_res_id=some-guid" in httpretty.last_request().body


@httpretty.activate
def test_app_service():
    """App Service environment: MSI_ENDPOINT, MSI_SECRET set"""

    expected_secret = "expected-secret"

    access_token = "AccessToken"
    url = "http://localhost:42/token"

    token_json = json.dumps({"access_token": access_token, "expires_on": int(time.time() + 3600)})
    httpretty.register_uri(httpretty.GET, url, body=token_json, content_type="application/json")

    with mock.patch("os.environ", {MSI_ENDPOINT: url, MSI_SECRET: expected_secret}):
        token = ManagedIdentityCredential().get_token("scope")
        assert token == access_token
        assert httpretty.last_request().headers["secret"] == expected_secret
        assert len(httpretty.httpretty.latest_requests) == 1

        # try a user assigned identity
        httpretty.register_uri(
            httpretty.GET,
            url + "?client_id=some-guid",
            body=token_json,
            content_type="application/json",
            match_query=True,
        )
        token = ManagedIdentityCredential(user_assigned_identity={"client_id": "some-guid"}).get_token("scope")
        assert token == access_token
        assert httpretty.last_request().headers["secret"] == expected_secret
        assert len(httpretty.httpretty.latest_requests) == 2


@httpretty.activate
def test_imds():
    access_token = "AccessToken"

    class reqs:
        count = 0

    def request_callback(request, uri, response_headers):
        reqs.count += 1
        if reqs.count == 1:
            # credential is probing to determine endpoint availability
            return 400, response_headers, json.dumps({})

        assert request.headers["Metadata"] == "true"
        json_payload = {"access_token": access_token, "expires_on": int(time.time() + 3600)}
        return 200, response_headers, json.dumps(json_payload)

    httpretty.register_uri(httpretty.GET, Endpoints.IMDS, body=request_callback, content_type="application/json")

    token = ManagedIdentityCredential().get_token("scope")
    assert token == access_token
