# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Provide access to settings for globally used Azure configuration values.
"""
from importlib import import_module
from typing import (
    Any,
    Dict,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
    TYPE_CHECKING
)

from azure.core.settings import settings as global_settings, Settings

from ._client_settings import (
    ClientSettings,
    AsyncClientSettings,
    SyncClient,
    AsyncClient,
    CredentialInputTypes,
    TransportInputTypes,
)
from ._resource_map import *


ClientType = TypeVar('ClientType', bound=SyncClient)


class Resources:

    def __init__(self) -> None:
        self._resources: Dict[str, ClientSettings] = {}

    @overload
    def get(self, resource: Literal['blobstorage']) -> ClientSettings['BlobServiceClient']:
        ...
    @overload
    def get(self, resource: Literal['blobcontainer']) -> ClientSettings['ContainerClient']:
        ...
    @overload
    def get(self, resource: Literal['tablestorage']) -> ClientSettings['TableServiceClient']:
        ...
    @overload
    def get(self, resource: Literal['servicebus']) -> ClientSettings['ServiceBusClient']:
        ...
    @overload
    def get(self, resource: Literal['openai']) -> ClientSettings['AzureOpenAI']:
        ...
    @overload
    def get(self, resoruce: str, *, cls: Type[ClientType]) -> ClientSettings[ClientType]:
        ...
    def get(
            self,
            resource: str,
            *,
            cls: Optional[Type[SyncClient]] = None,
            transport: Optional[TransportInputTypes] = None,
            api_version: Optional[str] = None,
            settings: Optional[Settings] = None,
            client_options: Optional[Dict[str, Any]] = None,
    ) -> ClientSettings:
        try:
            resource_settings = self._resources[resource]
            if cls:
                resource_settings.cls.set_value(cls)
            if transport:
                resource_settings.transport.set_value(transport)
            if api_version:
                resource_settings.api_version.set_value(api_version)
            if client_options:
                resource_settings.client_options.set_value(client_options)
            return resource_settings
        except KeyError:
            pass
        try:
            new_resource_config = RESOURCE_SDK_MAP[resource]
        except KeyError as e:
            raise ValueError(f"Resource type '{resource}' has no matching SDK client.") from e
        if not settings:
            settings = global_settings
        if not cls and not new_resource_config[1]:
            raise ValueError(f"No default client type configured for '{resource}'. Please provide 'cls'.")
        new_resource = ClientSettings(
            env_prefix="AZURE_" + new_resource_config[0].upper(),
            cls=cls or new_resource_config[1],
            transport=transport,
            api_version=api_version,
            settings=settings,
            resource=resource,
            client_options=client_options
        )
        self._resources[resource] = new_resource
        return new_resource


class AsyncResources:

    def __init__(self) -> None:
        self._resources: Dict[str, AsyncClientSettings] = {}

    def get(self, resource: str) -> AsyncClientSettings:
        try:
            return self._resources[resource]
        except KeyError:
            pass
        try:
            new_resource_config = _RESOURCE_SDK_ASYNC_MAP[resource]
        except KeyError as e:
            raise ValueError(f"Unexpected resource type: {resource}") from e
        new_resource = ClientSettings(
            globals=self,
            env_prefix="AZURE_" + new_resource_config[0].upper(),
            cls=new_resource_config[1]
        )
        self._resources[resource] = new_resource
        return new_resource

    def dump(self) -> Dict[str, Any]:
        output = {}
        for key, value in self._resources.items():
            output[key] = value.dump()
        return output

    def load(self, intput: Dict[str, Any]) -> None:
        raise NotImplementedError()

resources: Resources = Resources()
"""The resources unique instance.

:type resources: Resources
"""
aresources: AsyncResources = AsyncResources()
"""The resources unique instance for async configuration.

:type aresources: AsyncResources
"""

__all__ = ('resources', 'Resources')