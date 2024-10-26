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
from __future__ import annotations
from itertools import takewhile, zip_longest as zip
import json
from typing import (
    Awaitable,
    runtime_checkable,
    Type,
    Optional,
    Callable,
    Union,
    Dict,
    Any,
    TypeVar,
    Generic,
    Protocol,
    Literal,
)
from typing_extensions import Self
from importlib import import_module
from collections import UserString
from inspect import getfullargspec

from azure.core.utils import parse_connection_string
from azure.core.pipeline.transport import HttpTransport, AsyncHttpTransport
from azure.core.credentials import (
    SupportsTokenInfo,
    AzureKeyCredential,
    AzureSasCredential,
    AzureNamedKeyCredential
)
from azure.core.credentials_async import AsyncSupportsTokenInfo
from azure.core.settings import _unset, PrioritizedSetting, Settings

from ._setting import StoredPrioritizedSetting
from ._resource_map import AUDIENCES

CredentialTypes = Union[
    AzureKeyCredential,
    AzureNamedKeyCredential,
    AzureSasCredential,
]

@runtime_checkable
class SyncClient(Protocol):
    def __init__(
            self,
            endpoint: str,
            credential: Any,
            *args,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            scope: Optional[str] = None,
            audience: Optional[str] = None,
            **kwargs
    ) -> None:
        ...
    def close(self) -> None:
        ...


@runtime_checkable
class AsyncClient(Protocol):
    def __init__(
            self,
            endpoint: str,
            credential: Any,
            *args,
            transport: Optional[AsyncHttpTransport] = None,
            api_version: Optional[str] = None,
            scope: Optional[str] = None,
            audience: Optional[str] = None,
            **kwargs
    ) -> None:
        ...
    async def close(self) -> None:
        ...


ClientType = TypeVar("ClientType", bound=SyncClient)
AsyncClientType = TypeVar("AsyncClientType", bound=AsyncClient)
CredentialInputTypes = Union[
    CredentialTypes,
    Type[AzureKeyCredential],
    Type[AzureNamedKeyCredential],
    Type[AzureSasCredential],
    SupportsTokenInfo,
    Callable[[], SupportsTokenInfo],
    Literal['default'],
]
AsyncCredentialInputTypes = Union[
    CredentialTypes,
    Type[AzureKeyCredential],
    Type[AzureNamedKeyCredential],
    Type[AzureSasCredential],
    AsyncSupportsTokenInfo,
    Type[AsyncSupportsTokenInfo],
    Callable[[], AsyncSupportsTokenInfo],
    Callable[[], Awaitable[AsyncSupportsTokenInfo]],
    Literal['default'],
]
TransportInputTypes = Union[
    HttpTransport,
    Callable[[], HttpTransport],
    Literal['default', 'requests']
]
AsyncTransportInputTypes = Union[
    AsyncHttpTransport,
    Callable[[], AsyncHttpTransport],
    Literal['default', 'aiohttp', 'httpx'],
]

def _convert_dict(value: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(value, str):
        return json.loads(value)
    return dict(value)


def _convert_str_from_setting(value: Union[str, PrioritizedSetting[Any, str]]) -> str:
    try:
        return value()
    except TypeError:
        return str(value)


def _convert_cls_from_setting(value: Union[PrioritizedSetting[Any, Type[SyncClient]], Type[SyncClient]]) -> Type[SyncClient]:
    if isinstance(value, PrioritizedSetting):
        return value()
    if isinstance(value, str):
        module, _, obj = value.rpartition('.')
        try:
            loaded_module = import_module(module)
            return getattr(module, obj)
        except (ImportError, AttributeError):
            pass
        raise ImportError(f"Unable to load '{obj}' from '{module}'")
    return value


def _convert_to_str(value: Any, include_sensitive: bool = False) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, type):
        module_path = value.__module__.split('.')
        public_path = ".".join(takewhile(lambda x: not x.startswith('_'), module_path))
        return public_path + f".{value.__name__}"
    if isinstance(value, dict):
        return json.dumps(value)
    raise RuntimeError("Value cannot be stored.")


def _convert_sync_transport(value: TransportInputTypes) -> Optional[HttpTransport]:
    if value.lower() == 'default':
        return None
    if isinstance(value, HttpTransport):
        return value
    raise ValueError(f"Unexpected transport type: '{value}'.")


class AutoUpdateValue(UserString):
    def __init__(self, value: PrioritizedSetting) -> None:
        self._setting = value
    @property
    def data(self) -> str:
        return self._setting()


class _SDKSettings:

    name: PrioritizedSetting[str, str]

    key: PrioritizedSetting[str, str]

    sas_token: PrioritizedSetting[str, str]

    endpoint: PrioritizedSetting[str, str]

    api_version: PrioritizedSetting[Union[PrioritizedSetting[Any, str], str], str]

    client_options: PrioritizedSetting[Dict[str, Any], Dict[str, Any]]

    def __init__(
            self,
            *,
            env_prefix: str,
            name: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            api_version: Optional[Union[str, PrioritizedSetting[Any, str]]] = None,
            settings: Settings,
            resource: str,
    ) -> None:
        self._prefix = env_prefix.rstrip('_').upper()
        self._resources: Dict[str, ClientSettings] = {}
        self._settings = settings
        self._resource = resource
        self.name = StoredPrioritizedSetting(
            'name',
            env_var=self._prefix + '_NAME',
            convert=str,
            default=name or _unset,
        )
        self.key = StoredPrioritizedSetting(
            name='key',
            env_var=self._prefix + '_API_KEY',
            convert=str
        )
        self.sas_token = StoredPrioritizedSetting(
            name='sas_token',
            env_var=self._prefix + '_SASTOKEN',
            convert=str
        )
        self.api_version = StoredPrioritizedSetting(
            name='api_version',
            env_var=self._prefix + '_API_VERSION',
            convert=_convert_str_from_setting,
            to_str=_convert_to_str
        )
        if api_version:
            self.api_version.set_value(api_version)
        self.endpoint = StoredPrioritizedSetting(
            name='endpoint',
            env_var=self._prefix + '_ENDPOINT',
            convert=str
        )
        self.client_options = StoredPrioritizedSetting(
            name='client_options',
            convert=_convert_dict,
            to_str=_convert_to_str
        )
        if client_options:
            self.client_options.set_value(client_options)


class ClientSettings(_SDKSettings, Generic[ClientType]):

    credential: PrioritizedSetting[CredentialInputTypes, Union[CredentialTypes, SupportsTokenInfo]]

    transport: PrioritizedSetting[
        Union[PrioritizedSetting[Any, Optional[HttpTransport]], TransportInputTypes], Optional[HttpTransport]
    ]

    cls: PrioritizedSetting[Union[PrioritizedSetting[Any, Type[ClientType]], Type[ClientType]], Type[ClientType]]

    def __init__(
            self,
            *,
            cls: Union[PrioritizedSetting[Any, Type[ClientType]], Type[ClientType]],
            env_prefix: str,
            name: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            api_version: Optional[Union[str, PrioritizedSetting[Any, str]]] = None,
            transport: Optional[Union[PrioritizedSetting[Any, Optional[HttpTransport]], TransportInputTypes]] = None,
            settings: Settings,
            resource: str,
    ) -> None:
        super().__init__(
            env_prefix=env_prefix,
            name=name,
            api_version=api_version,
            client_options=client_options,
            settings=settings,
            resource=resource
        )
        self.transport = StoredPrioritizedSetting(
            name='transport',
            env_var='AZURE_SDK_TRANSPORT',
            convert=self._build_transport,
            default=transport or _unset,
            to_str=_convert_to_str
        )
        if transport:
            self.transport.set_value(transport)
        self.cls = StoredPrioritizedSetting(
            name='cls',
            convert=_convert_cls_from_setting,
            to_str=_convert_to_str
        )
        if cls:
            self.cls.set_value(cls)
        self.credential = StoredPrioritizedSetting(
            name='credential',
            default='default',
            convert=self._build_credential,
            to_str=_convert_to_str
        )

    def __getitem__(self, name: str) -> Self:
        if name in self.__dict__:
            raise ValueError(
                "Name is not supported. "
                f"Please use a name that doesn't conflict with a Client setting: {self.__dict__.keys()}"
            )
        try:
            return self._resources[name]
        except KeyError:
            new_resource = self.__class__(
                cls=self.cls,
                env_prefix=self._prefix + f'_{name.upper()}',
                name=name,
                transport=self.transport,
                api_version=self.api_version,
                settings=self._settings,
                resource=self._resource
            )
            self._resources[name] = new_resource
            return new_resource

    def _build_credential(self, value: CredentialInputTypes) -> Union[CredentialTypes, SupportsTokenInfo]:
        try:
            if value.lower() == 'default':
                from azure.identity import DefaultAzureCredential
                return DefaultAzureCredential()
        except AttributeError:
            if isinstance(value, (SupportsTokenInfo, AzureKeyCredential, AzureNamedKeyCredential, AzureSasCredential)):
                return value
            if value is AzureKeyCredential:
                return AzureKeyCredential(self.key())
            if value is AzureSasCredential:
                return AzureSasCredential(self.sas_token())
            if value is AzureNamedKeyCredential:
                return AzureNamedKeyCredential(self.name(), self.key())
        try:
            return value()
        except TypeError:
            pass
        raise ValueError(f'Cannot convert {value} to credential type.')

    def client(
            self,
            *,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            cls: Optional[Type[ClientType]] = None,
            endpoint: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None
    ) -> ClientType:
        """Return the authenticated client.

        :rtype: namedtuple
        :returns: The current values for all settings, with values overridden by parameter values

        Examples:

        .. code-block:: python

           # return current settings with log level overridden
           settings.config(log_level=logging.DEBUG)

        """
        try:
            new_client_options = self.client_options()
        except RuntimeError:
            new_client_options = {}
        new_client_options.update(client_options or {})
        kwargs = {}
        endpoint = self.endpoint(endpoint)
        credential = self.credential(credential)
        try:
            kwargs['transport'] = self.transport(transport)
        except RuntimeError:
            pass
        try:
            kwargs['api_version'] = self.api_version(api_version)
        except RuntimeError:
            pass

        try:
            token_scope = AUDIENCES[self._resource][self._settings.azure_cloud()]
        except (KeyError, RuntimeError):
            raise ValueError(
                f"Cannot find auth scope for {self._resource} with {self._settings.azure_cloud().value}."
            )

        cls = self.cls(cls)
        spec = getfullargspec(cls)

        if len(spec.args) > 1:
            if spec.defaults:
                cls_args = reversed(list(zip(reversed(spec.args), reversed(spec.defaults), fillvalue=_unset)))
            else:
                cls_args = zip(spec.args, [], fillvalue=_unset)
            for name, default in cls_args:
                if name == 'endpoint' or name.endswith('_endpoint') or name.endswith('_url'):
                    kwargs[name] = endpoint
                elif name == 'credential':
                    kwargs[name] = credential
                else:
                    if default is _unset and name not in client_options and name != 'self':
                        raise ValueError(f"Missing required positional parameter: '{name}'.")

        cls_kwargs = {a: spec.kwonlydefaults.get(a, _unset) for a in spec.kwonlyargs}
        for name, default in cls_kwargs.items():
            if name == 'endpoint' or name.endswith('_endpoint') or name.endswith('_url') and not kwargs:
                kwargs[name] = endpoint
            elif name == 'credential':
                kwargs[name] = credential
            elif name.endswith('api_key') and hasattr(credential, 'key') and 'credential' not in cls_kwargs and 'credential' not in kwargs:
                kwargs[name] = credential.key
            elif name.endswith('token_provider') and hasattr(credential, 'get_token') and 'credential' not in cls_kwargs and 'credential' not in kwargs:
                from azure.identity import get_bearer_token_provider    
                kwargs[name] = get_bearer_token_provider(credential, token_scope)
            elif name == 'audience':
                kwargs[name] = token_scope.rstrip('/.default')
            elif name == 'scope':
                kwargs[name] = token_scope
            else:
                if default is _unset and name not in client_options:
                    raise ValueError(f"Missing required keyword parameter: '{name}'.")
        kwargs.update(new_client_options)
        return cls(**kwargs)


class AsyncClientSettings(_SDKSettings, Generic[AsyncClientType]):

    credential: PrioritizedSetting[AsyncCredentialInputTypes, Union[CredentialTypes, AsyncSupportsTokenInfo]]

    transport: PrioritizedSetting[AsyncTransportInputTypes, Optional[AsyncHttpTransport]]

    cls: PrioritizedSetting[Union[str, Type[AsyncClientType]], Type[AsyncClientType]]

    def __init__(
            self,
            *,
            cls: Union[str, Type[ClientType]],
            env_prefix: str,
            name: Optional[str] = _unset,
            transport: Optional[TransportInputTypes] = _unset,
    ) -> None:
        super().__init__(
            env_prefix=env_prefix,
            name=name
        )
        self.transport = StoredPrioritizedSetting(
            name='transport',
            env_var='AZURE_SDK_ASYNC_TRANSPORT',
            convert=self._build_transport,
            default=transport
        )
        self.cls = StoredPrioritizedSetting(
            name='cls',
            env_var=self._prefix + '_ASYNC_CLIENT_CLS',
            default=cls,
            convert=self._convert_clientcls
        )
        self.credential = StoredPrioritizedSetting(
            name='credential',
            env_var=None,
            default='Default',
            convert=self._build_credential
        )

    def __getitem__(self, name: str) -> Self:
        try:
            return self._resources[name]
        except KeyError:
            new_resource = self.__class__(
                cls=self.cls(),
                env_prefix=self._prefix + f'_{name.upper()}',
                name=name,
                transport=self.transport.default
            )
            self._resources[name] = new_resource
            return new_resource

    def _convert_clientcls(self, value: Union[str, Type[AsyncClient]]) -> Type[AsyncClient]:
        if isinstance(value, str):
            module, _, obj = value.rpartition('.')
            return _load_class(obj, module)
        return value

    def _build_credential(self, value: CredentialInputTypes) -> Union[CredentialTypes, AsyncSupportsTokenInfo]:
        try:
            value = value.lower()
        except AttributeError:
            if isinstance(value, AsyncSupportsTokenInfo):
                return value
        else:
            if value == 'default':
                from azure.identity.aio import DefaultAzureCredential
                return DefaultAzureCredential()
            if value == 'azurekeycredential':
                return AzureKeyCredential(self.key)
            if value == 'azuresascredential':
                return AzureSasCredential(self.sas_token)
            if value == 'azurenamedkeycredential':
                return AzureNamedKeyCredential(self.name, self.key)
        try:
            return value()
        except TypeError:
            pass
        raise ValueError(f'Cannot convert {value} to credential type.')

    def _build_transport(self, value: TransportInputTypes) -> Optional[AsyncHttpTransport]:
        if value.lower() == 'default':
            return None
        if value == 'httpx':
            raise NotImplementedError()
        if value == 'asyncio':
            raise NotImplementedError()
        if isinstance(value, AsyncHttpTransport):
            return value
        raise ValueError(f"Unexpected transport type: '{value}'.")

    def client(
            self,
            *,
            transport: Optional[AsyncTransportInputTypes] = None,
            credential: Optional[AsyncCredentialInputTypes] = None,
            cls: Optional[Type[AsyncClientType]] = None,
            endpoint: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None
    ) -> AsyncClientType:
        """Return the authenticated client.

        :rtype: namedtuple
        :returns: The current values for all settings, with values overridden by parameter values

        Examples:

        .. code-block:: python

           # return current settings with log level overridden
           settings.config(log_level=logging.DEBUG)

        """
        endpoint = self.endpoint(endpoint)
        try:
            transport = self.transport(transport)
        except RuntimeError:
            transport = None

        credential = self.credential(credential)
        cls = self.cls(cls)
        return cls(endpoint, credential=credential, **client_options or {})
