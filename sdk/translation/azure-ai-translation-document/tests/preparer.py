# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer, get_credential


DocumentTranslationPreparer = functools.partial(
    PowerShellPreparer,
    "translation",
    document_translation_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    document_translation_storage_name="fakeendpoint",
    document_translation_storage_key="fakeZmFrZV9hY29jdW50X2tleQ==",
)


class DocumentTranslationClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super().__init__(name_prefix="", random_name_length=42)
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        doctranslation_test_endpoint = kwargs.get("document_translation_endpoint")

        # set polling interval to 0 for recorded tests
        if not self.is_live:
            self.client_kwargs["polling_interval"] = 0

        client = self.client_cls(doctranslation_test_endpoint, get_credential(), **self.client_kwargs)
        kwargs.update({"client": client})
        return kwargs
