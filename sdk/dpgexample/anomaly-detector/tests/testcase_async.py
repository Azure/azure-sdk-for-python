# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.ai.anomalydetector.aio import AnomalyDetectorClient


class AnomalydetectorAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(AnomalydetectorAsyncTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(AnomalyDetectorClient, is_async=True)
        return self.create_client_from_credential(
            AnomalyDetectorClient,
            credential=credential,
            endpoint=endpoint,
        )
