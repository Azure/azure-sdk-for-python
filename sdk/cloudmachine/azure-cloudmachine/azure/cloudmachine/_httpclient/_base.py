# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import Any, Dict, Optional, Union
from typing_extensions import Self
from concurrent.futures import Executor

from azure.core import PipelineClient
from azure.core.credentials import (
    AzureKeyCredential,
    AzureNamedKeyCredential,
    AzureSasCredential,
    SupportsTokenInfo
)
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.identity import DefaultAzureCredential
from azure.core.rest import HttpRequest, HttpResponse

from ..provisioning._resource import generate_envvar
from ._config import CloudMachinePipelineConfig
from ._auth_policy import BearerTokenChallengePolicy
from ._api_versions import DEFAULT_API_VERSIONS


class CloudMachineClientlet:
    _id: str

    def __init__(
            self,
            endpoint: str,
            credential: Union[AzureKeyCredential, AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo],
            *,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            executor: Optional[Executor] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            scope: str,
            **kwargs
    ):
        self._credential = credential
        self._endpoint = endpoint.rstrip('/')

        auth_policy = BearerTokenChallengePolicy(
            self._credential,
            *scope
        )
        # TODO: Need to be able to swap out auth policy of existing config
        self._config = config or CloudMachinePipelineConfig(
            authentication_policy=auth_policy,
            transport=transport,
            api_version=api_version or DEFAULT_API_VERSIONS[self._id],
            **kwargs
        )
        self._client = PipelineClient(
            base_url=endpoint,
            pipeline=self._config.pipeline,
        )
        self._executor = executor

    def close(self) -> None:
        self._client.close()

    def _send_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        path_format_arguments = {
            "endpoint": self._endpoint
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)
        response = self._client.send_request(request, **kwargs)
        response.raise_for_status()
        return response
