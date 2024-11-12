# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import Any, Dict, Optional, Union, Self, Type
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

from .._resources._client_settings import ClientSettings
from .._resources._resource_map import RESOURCE_SDK_MAP, DEFAULT_API_VERSIONS
from ..provisioning._resource import generate_envvar
from ._config import CloudMachinePipelineConfig
from ._auth_policy import BearerTokenChallengePolicy


class CloudMachineClientlet:
    _id: str
    resource_settings: ClientSettings[Type[Self]]
    resource_id: Optional[str]

    def __init__(
            self,
            endpoint: str,
            credential: Union[AzureKeyCredential, AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo],
            *,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            executor: Optional[Executor] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            resource_id: Optional[str] = None,
            scope: str,
            **kwargs
    ):
        self._credential = credential
        self._endpoint = endpoint.rstrip('/')

        auth_policy = BearerTokenChallengePolicy(
            self._credential,
            scope
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

    # def resource_id(self) -> str:
    #     # TODO Fix this so that it works for any resource ID.
    #     for envvar in RESOURCE_SDK_MAP[self._id][0]:
    #         try:
    #             return os.environ[f"AZURE_CLOUDMACHINE_{envvar.upper()}_ID"]
    #         except KeyError:
    #             continue
    #     raise ValueError(f"No resource ID found for {self._id}")

    def _send_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        path_format_arguments = {
            "endpoint": self._endpoint
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)
        response = self._client.send_request(request, **kwargs)
        response.raise_for_status()
        return response
