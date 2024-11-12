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
from typing import (
    Any,
    Dict,
    Literal,
    Optional,
    Type,
    TypeVar,
    Callable,
    overload,
    TYPE_CHECKING
)

from azure.core.settings import settings as global_settings, Settings

from ._client_settings import (
    ClientSettings,
    StorageClientSettings,
    OpenAiClientSettings,
    SearchClientSettings,
    SyncClient,
    CredentialInputTypes,
    TransportInputTypes,
)
from ._resource_map import *


ClientType = TypeVar('ClientType', bound=SyncClient)


class Resources:

    @overload
    def get(self, resource: Literal['storage:blob']) -> StorageClientSettings[BlobServiceClient]:
        ...
    @overload
    def get(self, resource: Literal['storage:blob:container']) -> StorageClientSettings[ContainerClient]:
        ...
    @overload
    def get(self, resource: Literal['storage:table']) -> ClientSettings[TableServiceClient]:
        ...
    @overload
    def get(self, resource: Literal['servicebus']) -> ClientSettings[ServiceBusClient]:
        ...
    @overload
    def get(self, resource: Literal['openai']) -> OpenAiClientSettings[AzureOpenAI]:
        ...
    @overload
    def get(self, resource: Literal['documentai']) -> ClientSettings[DocumentIntelligenceClient]:
        ...
    @overload
    def get(self, resource: Literal['search']) -> SearchClientSettings[SearchIndexClient]:
        ...
    @overload
    def get(self, resource: Literal['search:index']) -> SearchClientSettings[SearchClient]:
        ...
    @overload
    def get(self, resource: Literal['keyvault:keys']) -> ClientSettings[KeyClient]:
        ...
    @overload
    def get(self, resource: Literal['keyvault:secrets']) -> ClientSettings[SecretClient]:
        ...
    @overload
    def get(self, resource: str, *, cls: Callable[[], ClientType]) -> ClientSettings[ClientType]:
        ...
    @overload
    def get(self, resource: str) -> ClientSettings:
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
            new_resource_config = RESOURCE_SDK_MAP[resource]
        except KeyError as e:
            raise ValueError(f"Resource type '{resource}' has no matching SDK client.") from e
        if not settings:
            settings = global_settings
        if not cls and not new_resource_config[1]:
            raise ValueError(f"No default client type configured for '{resource}'. Please provide 'cls'.")
        new_resource = ClientSettings(
            env_prefix=new_resource_config[0],
            cls=cls or new_resource_config[1],
            transport=transport,
            api_version=api_version,
            settings=settings,
            resource=resource,
            client_options=client_options
        )
        return new_resource



resources: Resources = Resources()
"""The resources unique instance.

:type resources: Resources
"""

__all__ = ('resources', 'Resources')