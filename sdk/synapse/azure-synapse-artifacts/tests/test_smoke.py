# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from testcase import SynapseArtifactsTest, ArtifactsClientPowerShellPreparer
from azure.core.exceptions import HttpResponseError

class SynapseArtifactsSmokeTest(SynapseArtifactsTest):

    # If endpoint is not unauthorized, `HttpResponseError` will be raised
    @ArtifactsClientPowerShellPreparer()
    def test_artifacts_workspace(self, artifacts_endpoint):
        client = self.create_client(endpoint=artifacts_endpoint)
        with pytest.raises(HttpResponseError) as e:
            client.workspace.get()
        assert e.value.status_code == 403
