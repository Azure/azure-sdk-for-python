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
from itertools import takewhile, zip_longest as zip, product
import json
from typing import (
    Awaitable,
    Mapping,
    runtime_checkable,
    Type,
    Optional,
    Callable,
    Union,
    Dict,
    List,
    Any,
    TypeVar,
    Generic,
    Protocol,
    Literal,
    overload
)
from typing_extensions import Self
from importlib import import_module
from collections import UserString
from inspect import getfullargspec

from azure.core.utils import case_insensitive_dict
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
from ._resource_map import *

CredentialTypes = Union[
    AzureKeyCredential,
    AzureNamedKeyCredential,
    AzureSasCredential,
]
SettingsTypes = Union[str, int, float, bool, None]
SettingT = TypeVar("SettingT", bound=SettingsTypes)


@runtime_checkable
class SyncClient(Protocol):

    def __init__(
            self,
            endpoint: str,
            *args: Any,
            credential: Any,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            **kwargs
    ) -> None:
        ...
    def close(self) -> None:
        ...

@runtime_checkable
class SyncClientWithSettings(Protocol):

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
    @property
    def client_settings(self) -> ClientSettings[Self]:
        ...
    def close(self) -> None:
        ...


ClientType = TypeVar("ClientType", bound=SyncClient)

CredentialInputTypes = Union[
    CredentialTypes,
    Type[AzureKeyCredential],
    Type[AzureNamedKeyCredential],
    Type[AzureSasCredential],
    SupportsTokenInfo,
    Callable[[], SupportsTokenInfo],
    Literal['default', 'AzureKeyCredential', 'AzureNamedKeyCredential', 'AzureSasCredential'],
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
    Literal['requests']
]
AsyncTransportInputTypes = Union[
    AsyncHttpTransport,
    Callable[[], AsyncHttpTransport],
    Literal['aiohttp', 'httpx'],
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
    if isinstance(value, PrioritizedSetting):
        return _convert_to_str(value())
    raise RuntimeError("Value cannot be stored.")


def _convert_sync_transport(value: TransportInputTypes) -> Optional[HttpTransport]:
    if isinstance(value, HttpTransport):
        return value
    # TODO: support custom str like 'requests'?
    try:
        return value()
    except TypeError:
        pass
    raise ValueError(f"Unexpected transport type: '{value}'.")


def _build_envs(prefixes: List[str], suffixes: List[str], name: Optional[str] = None) -> List[str]:
    all_vars = product(prefixes, suffixes)
    general_prefix = ['AZURE', name] if name else ['AZURE']
    return ["_".join(general_prefix + list(var)).upper() for var in all_vars]


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

    api_version: PrioritizedSetting[Union[PrioritizedSetting[str, str], str], str]

    audience: PrioritizedSetting[Union[PrioritizedSetting[str, str], str], str]

    client_options: PrioritizedSetting[Dict[str, Any], Dict[str, Any]]

    resource_name: str

    setting_name: Optional[str]

    def __init__(
            self,
            *,
            env_prefix: List[str],
            setting_name: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            api_version: Optional[Union[str, PrioritizedSetting[str, str]]] = None,
            audience: Optional[Union[str, PrioritizedSetting[str, str]]] = None,
            settings: Settings,
            resource: str,
            extra_settings: Optional[Dict[str, PrioritizedSetting]] = None
    ) -> None:
        self._prefixes = env_prefix
        self._resources: Dict[str, ClientSettings] = {}
        self._global_settings = settings
        self.resource_name = resource
        self.setting_name = setting_name
        self.name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME'], setting_name),
            convert=str,
        )
        self.key = StoredPrioritizedSetting(
            name='key',
            env_vars=_build_envs(self._prefixes, ['KEY', 'API_KEY'], setting_name),
            convert=str
        )
        self.resource_id = StoredPrioritizedSetting(
            name='resource_id',
            env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID'], setting_name),
            convert=self._build_resource_id,
            default='infer'
        )
        self.subscription_id = StoredPrioritizedSetting(
            name='subscription_id',
            env_var='AZURE_SUBSCRIPTION_ID',
            convert=str
        )
        self.resource_group = StoredPrioritizedSetting(
            name='resource_group',
            env_vars=_build_envs(self._prefixes, ['RESOURCE_GROUP'], setting_name),
            convert=str
        )
        self.sas_token = StoredPrioritizedSetting(
            name='sas_token',
            env_vars=_build_envs(self._prefixes, ['SASTOKEN', 'SAS_TOKEN'], setting_name),
            convert=str
        )
        self.api_version = StoredPrioritizedSetting(
            name='api_version',
            env_vars=_build_envs(self._prefixes, ['API_VERSION'], setting_name),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str
        )
        if api_version:
            self.api_version.set_value(api_version)
        self.audience = StoredPrioritizedSetting(
            name='audience',
            env_vars=_build_envs(self._prefixes, ['AUDIENCE'], setting_name),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str
        )
        if audience:
            self.audience.set_value(audience)
        self.endpoint = StoredPrioritizedSetting(
            name='endpoint',
            env_vars=_build_envs(self._prefixes, ['ENDPOINT'], setting_name),
            convert=str
        )
        self.client_options = StoredPrioritizedSetting(
            name='client_options',
            convert=_convert_dict,
            to_str=_convert_to_str,
            default={}
        )
        if client_options:
            self.client_options.set_value(client_options)
        self._settings: Dict[str, StoredPrioritizedSetting] = case_insensitive_dict(extra_settings) or case_insensitive_dict({})
        self._settings.update(
            {
                'name': self.name,
                'key': self.key,
                'resource_id': self.resource_id,
                'subscription_id': self.subscription_id,
                'resource_group': self.resource_group,
                'sas_token': self.sas_token,
                'api_version': self.api_version,
                'audience': self.audience,
                'endpoint': self.endpoint,
                'client_options': self.client_options
            }
        )

    def __contains__(self, value: str) -> bool:
        return value in self._settings

    def _build_resource_id(self, value: str) -> str:
        if value == 'infer':
            try:
                template = RESOURCE_IDS[self.resource_name]
                return template.format(
                    subscription_id=self.subscription_id,
                    resource_group=self.resource_group,
                    name=self.name
                )
            except (KeyError, RuntimeError):
                raise RuntimeError(f"Unable to build resource ID for '{self.resource_name}'.")
        elif isinstance(value, str):
            return value
        raise ValueError(f'Cannot convert {value} to resource ID.')

    def unset(self, name: str) -> None:
        if name in self._settings:
            self._settings[name].unset_value()
            return

    def set(self, name: str, value: SettingsTypes) -> None:
        if name in self._settings:
            self._settings[name].set_value(value)
            return
        new_setting = StoredPrioritizedSetting(
            name,
            env_vars=_build_envs(self._prefixes, [name.upper()], self.setting_name),
        )
        new_setting.set_value(value)
        self._settings[name] = new_setting

    @overload
    def get(self, name: Literal['name']) -> str:
        ...
    @overload
    def get(self, name: Literal['name'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: str, default: SettingT) -> SettingT:
        ...
    @overload
    def get(self, name: str, default: None) -> Optional[SettingsTypes]:
        ...
    @overload
    def get(self, name: str) -> SettingsTypes:
        ...
    def get(self, name, default = _unset):
        try:
            try:
                return self._settings[name]()
            except KeyError:
                new_setting = StoredPrioritizedSetting(
                    name,
                    env_vars=_build_envs(self._prefixes, [name.upper()], self.setting_name),
                )
                self._settings[name] = new_setting
                return new_setting()
        except RuntimeError:
            if default != _unset:
                return default
            raise

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, None]]:
        output = {}
        for setting in self._settings.values():
            try:
                key, value = setting.get_config()
                output[key] = value
            except RuntimeError:
                continue
        return output

    def add_config_store(self, config: Mapping[str, Any], position: Literal['first', 'last'] = 'first') -> None:
        for setting in self._settings.values():
            if position == 'first':
                setting.config_stores.insert(0, config)
            else:
                setting.config_stores.append(config)


class ClientSettings(_SDKSettings, Generic[ClientType]):

    credential: PrioritizedSetting[CredentialInputTypes, Union[CredentialTypes, SupportsTokenInfo]]

    transport: PrioritizedSetting[
        Union[PrioritizedSetting[Any, Optional[HttpTransport]], TransportInputTypes], Optional[HttpTransport]
    ]

    cls: PrioritizedSetting[Union[PrioritizedSetting[Any, Callable[..., ClientType]], Callable[..., ClientType]], Callable[..., ClientType]]

    def __init__(
            self,
            *,
            cls: Union[PrioritizedSetting[Any, Callable[..., ClientType]], Callable[..., ClientType]],
            env_prefix: List[str],
            setting_name: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            api_version: Optional[Union[str, PrioritizedSetting[str, str]]] = None,
            audience: Optional[Union[str, PrioritizedSetting[str, str]]] = None,
            transport: Optional[Union[PrioritizedSetting[Any, Optional[HttpTransport]], TransportInputTypes]] = None,
            settings: Settings,
            extra_settings: Optional[Dict[str, PrioritizedSetting]] = None,
            resource: str,
    ) -> None:
        super().__init__(
            env_prefix=env_prefix,
            setting_name=setting_name,
            api_version=api_version,
            client_options=client_options,
            settings=settings,
            resource=resource,
            audience=audience,
            extra_settings=extra_settings
        )
        self.transport = StoredPrioritizedSetting(
            name='transport',
            env_var='AZURE_SDK_TRANSPORT',
            convert=_convert_sync_transport,
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
            env_vars=_build_envs(self._prefixes, ['CREDENTIAL'], self.setting_name),
            convert=self._build_credential,
            to_str=_convert_to_str
        )

    def __getitem__(self, name: Optional[str]) -> ClientSettings[ClientType]:
        if name is None:
            return self
        try:
            return self._resources[name]
        except KeyError:
            new_resource = self.__class__(
                cls=self.cls,
                env_prefix=self._prefixes,
                setting_name=name,
                transport=self.transport,
                api_version=self.api_version,
                settings=self._global_settings,
                resource=self.resource_name,
                client_options=self.client_options(),
                extra_settings=self._settings
            )
            self._resources[name] = new_resource
            return new_resource

    def _build_credential(self, value: CredentialInputTypes) -> Union[CredentialTypes, SupportsTokenInfo]:
        try:
            value = value.lower()
            if value == 'default':
                from azure.identity import DefaultAzureCredential
                return DefaultAzureCredential()
            if value == 'azurekeycredential':
                return AzureKeyCredential(self.key())
            if value == 'azuresascredential':
                return AzureSasCredential(self.sas_token())
            if value == 'azurenamedkeycredential':
                return AzureNamedKeyCredential(self.name(), self.key())
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

    def copy(
            self,
            *,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            cls: Optional[Type[ClientType]] = None,
            endpoint: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None
    ) -> ClientSettings[ClientType]:
        new_settings = ClientSettings(
            settings=self._global_settings,
            resource=self.resource_name,
            env_prefix=self._prefixes,
            extra_settings=self._settings,
            cls=cls or self.cls()
        )
        new_settings.endpoint.set_value(endpoint or self.endpoint)
        new_settings.api_version.set_value(api_version or self.api_version)
        new_settings.credential.set_value(credential or self.credential)
        new_settings.transport.set_value(transport or self.transport)
        new_settings.client_options.set_value(client_options or self.client_options)
        new_settings.key.set_value(self.key)
        new_settings.name.set_value(self.name)
        new_settings.resource_group.set_value(self.resource_group)
        new_settings.subscription_id.set_value(self.subscription_id)
        new_settings.resource_id.set_value(self.resource_id)
        new_settings.sas_token.set_value(self.sas_token)
        return new_settings

    def client(
            self,
            *,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            cls: Optional[Callable[..., ClientType]] = None,
            endpoint: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            audience: Optional[str] = None,
    ) -> ClientType:
        """Return the authenticated client.

        :rtype: namedtuple
        :returns: The current values for all settings, with values overridden by parameter values

        Examples:

        .. code-block:: python

           # return current settings with log level overridden
           settings.config(log_level=logging.DEBUG)

        """
        new_client_options = self.client_options()
        new_client_options.update(client_options or {})
        kwargs = {}
        try:
            endpoint = self.endpoint()
            credential = self.credential(credential)
            cls = self.cls(cls)
        except RuntimeError as e:
            raise RuntimeError(f"Unable to build client for {self.resource_name}: {e}.") from e
        try:
            kwargs['transport'] = self.transport(transport)
        except RuntimeError:
            pass
        try:
            kwargs['api_version'] = self.api_version(api_version)
        except RuntimeError:
            pass
        try:
            kwargs['audience'] = self.audience(audience)
        except RuntimeError:
            pass

        try:
            token_scope = AUDIENCES[self.resource_name][self._global_settings.azure_cloud()]
        except (KeyError, RuntimeError):
            raise ValueError(
                f"Cannot find auth scope for {self.resource_name} with {self._global_settings.azure_cloud().value}."
            )

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
                elif name != 'self':
                    try:
                        kwargs[name] = new_client_options.get(name) or self.get(name)
                    except RuntimeError as e:
                        if default is _unset:
                            raise ValueError(f"Missing required positional parameter: '{name}'.") from e

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
            #elif name == 'audience':
            #    kwargs[name] = token_scope.rstrip('/.default')
            elif name == 'scope':
                kwargs[name] = token_scope
            elif name not in new_client_options:
                try:
                    kwargs[name] = self.get(name)
                except RuntimeError:
                    if default is _unset:
                        raise ValueError(f"Missing required keyword parameter: '{name}'.")
                    
        kwargs.update(new_client_options)
        client = cls(**kwargs)
        return client


class StorageClientSettings(ClientSettings[ClientType]):
    def __getitem__(self, name: Optional[str]) -> StorageClientSettings[ClientType]:
        return super().__getitem__(name)

    @overload
    def set(self, name: Literal['container_name'], value: str) -> None:
        ...
    @overload
    def set(self, name: str, value: SettingsTypes) -> None:
        ...
    def set(self, name, value) -> None:
        super().set(name=name, value=value)

    @overload
    def unset(self, name: Literal['container_name']) -> None:
        ...
    @overload
    def unset(self, name: str) -> None:
        ...
    def unset(self, name):
        super().unset(name)

    @overload
    def get(self, name: Literal['container_name']) -> str:
        ...
    @overload
    def get(self, name: Literal['container_name'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: str, default: SettingT) -> SettingT:
        ...
    @overload
    def get(self, name: str, default: None) -> Optional[SettingsTypes]:
        ...
    @overload
    def get(self, name: str) -> SettingsTypes:
        ...
    def get(self, name: str, default = _unset) -> Any:
        return super().get(name=name, default=default)


class OpenAiClientSettings(ClientSettings[ClientType]):
    def __getitem__(self, name: Optional[str]) -> OpenAiClientSettings[ClientType]:
        return super().__getitem__(name)

    @overload
    def set(self, name: Literal['embeddings_model'], value: str) -> None:
        ...
    @overload
    def set(self, name: Literal['embeddings_deployment'], value: str) -> None:
        ...
    @overload
    def set(self, name: Literal['chat_model'], value: str) -> None:
        ...
    @overload
    def set(self, name: Literal['chat_deployment'], value: str) -> None:
        ...
    @overload
    def set(self, name: str, value: SettingsTypes) -> None:
        ...
    def set(self, name, value) -> None:
        super().set(name=name, value=value)

    @overload
    def unset(self, name: Literal['embeddings_model']) -> None:
        ...
    @overload
    def unset(self, name: Literal['embeddings_deployment']) -> None:
        ...
    @overload
    def unset(self, name: Literal['chat_model']) -> None:
        ...
    @overload
    def unset(self, name: Literal['chat_deployment']) -> None:
        ...
    @overload
    def unset(self, name: str) -> None:
        ...
    def unset(self, name):
        super().unset(name)

    @overload
    def get(self, name: Literal['embeddings_model']) -> str:
        ...
    @overload
    def get(self, name: Literal['embeddings_model'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: Literal['embeddings_deployment']) -> str:
        ...
    @overload
    def get(self, name: Literal['embeddings_deployment'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: Literal['chat_model']) -> str:
        ...
    @overload
    def get(self, name: Literal['chat_model'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: Literal['chat_deployment']) -> str:
        ...
    @overload
    def get(self, name: Literal['chat_deployment'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: str, default: SettingT) -> SettingT:
        ...
    @overload
    def get(self, name: str, default: None) -> Optional[SettingsTypes]:
        ...
    @overload
    def get(self, name: str) -> SettingsTypes:
        ...
    def get(self, name: str, default = _unset) -> Any:
        return super().get(name=name, default=default)


class SearchClientSettings(ClientSettings[ClientType]):
    def __getitem__(self, name: Optional[str]) -> SearchClientSettings[ClientType]:
        return super().__getitem__(name)

    @overload
    def set(self, name: Literal['index_name'], value: str) -> None:
        ...
    @overload
    def set(self, name: str, value: SettingsTypes) -> None:
        ...
    def set(self, name, value) -> None:
        super().set(name=name, value=value)

    @overload
    def unset(self, name: Literal['index_name']) -> None:
        ...
    @overload
    def unset(self, name: str) -> None:
        ...
    def unset(self, name):
        super().unset(name)

    @overload
    def get(self, name: Literal['index_name']) -> str:
        ...
    @overload
    def get(self, name: Literal['index_name'], default: Optional[str]) -> Optional[str]:
        ...
    @overload
    def get(self, name: str, default: SettingT) -> SettingT:
        ...
    @overload
    def get(self, name: str, default: None) -> Optional[SettingsTypes]:
        ...
    @overload
    def get(self, name: str) -> SettingsTypes:
        ...
    def get(self, name: str, default = _unset) -> Any:
        return super().get(name=name, default=default)
