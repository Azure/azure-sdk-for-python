# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import inspect
import functools

from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureMgmtPreparer, EnvironmentVariableLoader

import azure.ai.vision.face as Client
import azure.ai.vision.face.aio as AsyncClient

from _shared import helpers


class ClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(ClientPreparer, self).__init__(name_prefix="", random_name_length=24)
        self._client_kwargs = client_kwargs
        self._client_cls = client_cls
        self._client = None

    def create_resource(self, name, **kwargs):
        endpoint = helpers.get_face_endpoint(**kwargs)
        account_key = helpers.get_account_key(**kwargs)

        self._client = self._client_cls(endpoint, AzureKeyCredential(account_key))
        env_name = (
            self._client_kwargs["client_env_name"]
            if self._client_kwargs is not None
            and "client_env_name" in self._client_kwargs
            else "client"
        )

        kwargs.update({env_name: self._client})
        return kwargs

    def remove_resource(self, name, **kwargs):
        # User has to call `await close()` in the test case if it is a coroutine function.
        if not inspect.iscoroutinefunction(self._client.close):
            self._client.close()


FacePreparer = functools.partial(
    EnvironmentVariableLoader,
    "face",
    azure_face_api_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    azure_face_api_name="fakeaccountname",
    azure_face_api_account_key="fakeaccountkey",
)

FaceClientPreparer = functools.partial(ClientPreparer, Client.FaceClient)
FaceSessionClientPreparer = functools.partial(ClientPreparer, Client.FaceSessionClient)

# Async client
AsyncFaceClientPreparer = functools.partial(ClientPreparer, AsyncClient.FaceClient)
AsyncFaceSessionClientPreparer = functools.partial(
    ClientPreparer, AsyncClient.FaceSessionClient
)
