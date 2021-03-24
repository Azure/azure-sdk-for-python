
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


DocumentTranslationPreparer = functools.partial(
    PowerShellPreparer,
    'documenttranslation',
    documenttranslation_test_endpoint="https://redacted.cognitiveservices.azure.com/",
    documenttranslation_test_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    documenttranslation_name="redacted",
    documenttranslation_storage_name="redacted",
    documenttranslation_storage_key="fakeZmFrZV9hY29jdW50X2tleQ=="
)


class DocumentTranslationClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(DocumentTranslationClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        doctranslation_test_endpoint = kwargs.get("documenttranslation_test_endpoint")
        doctranslation_test_api_key = kwargs.get("documenttranslation_test_api_key")


        client = self.client_cls(
            doctranslation_test_endpoint,
            AzureKeyCredential(doctranslation_test_api_key),
            **self.client_kwargs
        )
        kwargs.update({"client": client})
        return kwargs
