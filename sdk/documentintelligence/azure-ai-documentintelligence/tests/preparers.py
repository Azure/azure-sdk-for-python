# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer
from azure.core.credentials import AzureKeyCredential

ENABLE_LOGGER = os.getenv("ENABLE_LOGGER", "False")
REGION = os.getenv("DOCUMENTINTELLIGENCE_LOCATION", None)


DocumentIntelligencePreparer = functools.partial(
    PowerShellPreparer,
    "documentintelligence",
    documentintelligence_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    documentintelligence_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    documentintelligence_storage_container_sas_url="https://blob_sas_url",
    documentintelligence_testing_data_container_sas_url="https://blob_sas_url",
    documentintelligence_multipage_storage_container_sas_url="https://blob_sas_url",
    documentintelligence_training_data_classifier_sas_url="https://blob_sas_url",
    documentintelligence_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/documentintelligencename",
    documentintelligence_region="region",
)


class GlobalClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(GlobalClientPreparer, self).__init__(name_prefix="", random_name_length=42)
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        if self.is_live:
            documentintelligence_endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
            documentintelligence_api_key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
            polling_interval = 5
        else:
            documentintelligence_endpoint = "https://fakeendpoint.cognitiveservices.azure.com"
            documentintelligence_api_key = "fakeZmFrZV9hY29jdW50X2tleQ=="
            polling_interval = 0

        client = self.client_cls(
            documentintelligence_endpoint,
            AzureKeyCredential(documentintelligence_api_key),
            polling_interval=polling_interval,
            logging_enable=True if ENABLE_LOGGER == "True" else False,
            **self.client_kwargs
        )
        kwargs.update({"client": client})
        return kwargs
