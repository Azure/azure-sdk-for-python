# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.core import PipelineClient
from azure.core.rest import HttpRequest, HttpResponse
from azure.identity import ClientSecretCredential

from helpers import GET_TOKEN_METHODS


class TestMultiTenantAuth(AzureRecordedTestCase):
    def _send_request(self, credential: ClientSecretCredential, get_token_method: str) -> HttpResponse:
        client = PipelineClient(base_url="https://graph.microsoft.com")
        token = getattr(credential, get_token_method)("https://graph.microsoft.com/.default")
        headers = {"Authorization": "Bearer " + token.token, "ConsistencyLevel": "eventual"}
        request = HttpRequest("GET", "https://graph.microsoft.com/v1.0/applications/$count", headers=headers)
        response = client.send_request(request)
        return response

    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        is_live() and not os.environ.get("AZURE_IDENTITY_MULTI_TENANT_CLIENT_ID"),
        reason="Multi-tenant envvars not configured.",
    )
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_multi_tenant_client_secret_graph_call(self, recorded_test, environment_variables, get_token_method):
        client_id = environment_variables.get("AZURE_IDENTITY_MULTI_TENANT_CLIENT_ID")
        tenant_id = environment_variables.get("AZURE_IDENTITY_MULTI_TENANT_TENANT_ID")
        client_secret = environment_variables.get("AZURE_IDENTITY_MULTI_TENANT_CLIENT_SECRET")
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        response = self._send_request(credential, get_token_method)
        assert response.status_code == 200
        assert int(response.text()) > 0
