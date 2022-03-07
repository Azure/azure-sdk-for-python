# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.synapse.artifacts import ArtifactsClient


class SynapseArtifactsTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(SynapseArtifactsTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint=None, **kwargs):
        credential = self.get_credential(ArtifactsClient)
        return self.create_client_from_credential(
            ArtifactsClient,
            credential=credential,
            endpoint=endpoint,
        )


ArtifactsClientPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "artifacts",
    artifacts_endpoint="https://myservice.artifacts.azure.com",
)
