# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.ai.anomalydetector import AnomalyDetectorClient


class AnomalydetectorTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(AnomalydetectorTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(AnomalyDetectorClient)
        return self.create_client_from_credential(
            AnomalyDetectorClient,
            credential=credential,
            endpoint=endpoint,
        )


AnomalydetectorPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "anomalydetector",
    anomalydetector_endpoint="https://myservice.azure.com"
)
