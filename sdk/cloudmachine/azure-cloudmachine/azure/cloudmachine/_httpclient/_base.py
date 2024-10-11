# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import Any, Dict, Optional, Self
from concurrent.futures import Executor

from azure.core import PipelineClient
from azure.core.pipeline.transport import HttpTransport
from azure.identity import DefaultAzureCredential
from azure.core.rest import HttpRequest, HttpResponse

from ..resources._resource import generate_envvar
from ._config import CloudMachinePipelineConfig
from ._auth_policy import BearerTokenChallengePolicy, TOKEN_AUTH_SCOPES
from ._api_versions import DEFAULT_API_VERSIONS


class CloudMachineClientlet:
    _id: str

    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            executor: Optional[Executor] = None,
            name: Optional[str] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            clients: Optional[Dict[str, Self]] = None,
            **kwargs
    ):
        # TODO: support other credential types?
        service_env = generate_envvar(self._id)
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_CLOUDMACHINE_{service_env}_{name}_ENDPOINT']
        else:
            endpoint = os.environ[f'AZURE_CLOUDMACHINE_{service_env}_ENDPOINT']

        self._clients = clients or {}
        self._endpoint = endpoint.rstrip('/')
        self._credential = DefaultAzureCredential()  # TODO Support key/connstr credentials
        auth_policy = BearerTokenChallengePolicy(
            self._credential,
            *TOKEN_AUTH_SCOPES[self._id]
        )
        # TODO: Need to be able to swap out auth policy of existing config
        self._config = config or CloudMachinePipelineConfig(
            authentication_policy=auth_policy,
            transport=transport,
            api_version=kwargs.pop('api_version', DEFAULT_API_VERSIONS[self._id]),
            **kwargs
        )
        self._client = PipelineClient(
            base_url=endpoint,
            pipeline=self._config.pipeline,
        )
        self._executor = executor

    def __getitem__(self, name) -> Self:
        try:
            return self._clients[name]
        except KeyError:
            pass
        try:
            client = self.__class__(
                name=name,
                executor=self._executor,
                config=self._config
            )
            self._clients[name] = client
            return client
        except KeyError:
            clsname = self.__class__.__name__
            raise KeyError(f"Unable to configure {clsname} for {name}")

    def close(self) -> None:
        self._client.close()

    def get_client(self, **kwargs) -> Any:
        raise NotImplementedError()

    def _send_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        path_format_arguments = {
            "endpoint": self._endpoint
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)
        response = self._client.send_request(request, **kwargs)
        response.raise_for_status()
        return response
