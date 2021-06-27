# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AsyncBearerTokenCredentialPolicy
from azure.core.credentials import AzureKeyCredential, AzureSasCredential

from .. import _constants as constants
from .._signature_credential_policy import EventGridSasCredentialPolicy

def _get_authentication_policy_async(credential):
    if credential is None:
        raise ValueError("Parameter 'self._credential' must not be None.")
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(
            credential,
            scopes=constants.DEFAULT_EVENTGRID_SCOPE
        )
    if isinstance(credential, AzureKeyCredential):
        return AzureKeyCredentialPolicy(
            credential=credential, name=constants.EVENTGRID_KEY_HEADER
        )
    if isinstance(credential, AzureSasCredential):
        return EventGridSasCredentialPolicy(
            credential=credential, name=constants.EVENTGRID_TOKEN_HEADER
        )
    raise ValueError(
        "The provided credential should be an instance of a TokenCredential, AzureSasCredential or AzureKeyCredential"
    )
