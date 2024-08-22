# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.ai.vision.face import (
    FaceClient,
    FaceSessionClient,
)
from azure.core.credentials import AzureKeyCredential


class FaceClientTestCase:
    def _set_up(self, endpoint, account_key) -> None:
        self._client = FaceClient(
            endpoint=endpoint, credential=AzureKeyCredential(account_key)
        )

    def _tear_down(self) -> None:
        self._client.close()


class FaceSessionClientTestCase:
    def _set_up(self, endpoint, account_key) -> None:
        self._client = FaceSessionClient(
            endpoint=endpoint, credential=AzureKeyCredential(account_key)
        )

    def _tear_down(self) -> None:
        self._client.close()
