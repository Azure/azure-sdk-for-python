# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Optional, Union

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import AzureNamedKeyCredential

from ._client import BatchClient as GenerateBatchClient
from .._patch import BatchExceptionPolicy, BatchSharedKeyAuthPolicy

__all__ = [
    "BatchClient",
]  # Add all objects you want publicly available to users at this package level


class BatchClient(GenerateBatchClient):
    """BatchClient.

    :param endpoint: The Azure Batch account endpoint.
    :type endpoint: str
    :param credential: The asynchronous token or Shared Key credential used to authenticate requests.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or
     ~azure.core.credentials.AzureNamedKeyCredential

    :keyword api_version: The service API version. Defaults to ``2026-10-01``.
     Overriding it may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureNamedKeyCredential, AsyncTokenCredential],
        *,
        api_version: Optional[str] = "2026-10-01",
        **kwargs
    ) -> None:
        per_call_policies = kwargs.pop("per_call_policies", [])
        per_call_policies.append(BatchExceptionPolicy())
        super().__init__(
            endpoint=endpoint,
            api_version=api_version,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", self._format_shared_key_credential(credential)),
            per_call_policies=per_call_policies,
            **kwargs
        )

    def _format_shared_key_credential(self, credential):
        if isinstance(credential, AzureNamedKeyCredential):
            return BatchSharedKeyAuthPolicy(credential)
        return None


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
