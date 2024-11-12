# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from enum import Enum
from typing import (
    Any,
    Dict,
    Generator,
    NamedTuple,
    Literal,
    Mapping,
    Optional,
    Protocol,
    Type,
    Callable,
    Union,
    Generic,
    Tuple,
    overload,
    TypeVar
)
from threading import Thread
from concurrent.futures import Executor, ThreadPoolExecutor

from dotenv import load_dotenv, dotenv_values

from azure.core.credentials import (
    AzureNamedKeyCredential,
    AzureSasCredential,
    SupportsTokenInfo,
)
from azure.core.pipeline.transport import HttpTransport
from azure.data.tables import TableServiceClient, TableClient

from ._resources._resources import resources as global_resources
from ._resources._resource_map import *
from ._resources._client_settings import (
    ClientSettings,
    StorageClientSettings,
    OpenAiClientSettings,
    SearchClientSettings,
    SyncClient,
    ClientType,
    TransportInputTypes,
    CredentialInputTypes
)
from .provisioning._deployment import azd_env_name, CloudMachineDeployment
from ._httpclient._eventlistener import EventListener
from ._httpclient import TransportWrapper
from ._httpclient._servicebus import CloudMachineServiceBus
from ._httpclient._config import CloudMachinePipelineConfig
from ._httpclient._storage import CloudMachineStorage
from ._httpclient._base import CloudMachineClientlet
from ._httpclient._documents import CloudMachineDocumentIndex

class _CMDefault(str, Enum):
    token = "0"


CloudmachineDefault = _CMDefault.token
ClientSettingsType = TypeVar("ClientSettingsType", bound=ClientSettings)

def load_dev_environment(name: str) -> Dict[str, str]:
    print("Loading local environment.")
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if not os.path.isdir(azd_dir):
        raise RuntimeError("No '.azure' directory found in current working dir. Please run 'azd init' with the Minimal template.")

    env_name = azd_env_name(name, 'local', None)
    env_loaded = load_dotenv(os.path.join(azd_dir, env_name, ".env"), override=True)
    if not env_loaded:
        raise RuntimeError(
            f"No cloudmachine infrastructure loaded for env: '{env_name}'.\n"
            " Please run 'flask cm run' to provision cloudmachine resources."
        )
    full_env = dotenv_values(os.path.join(azd_dir, env_name, ".env"))
    trimmed_env = {}
    for key, value in full_env.items():
        if key.startswith('AZURE_'):
            trimmed_env[key[6:]] = value
    return trimmed_env


class DataModel(Protocol):
    def __init__(self, **kwargs) -> None:
        ...

    @property
    def __table__(self) -> str:
        ...
    
    def model_dump(self, *, by_alias: bool = False, **kwargs) -> Dict[str, Any]:
        ...
    

class CloudMachineTableData(CloudMachineClientlet):
    _id: Literal['storage:table'] = 'storage:table'

    def __init__(
            self,
            endpoint: str,
            credential: Union[AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo],
            *,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            executor: Optional[Executor] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            scope: str,
            **kwargs
    ):
        # super().__init__(
        #     endpoint=endpoint,
        #     credential=credential,
        #     transport=transport,
        #     api_version=api_version,
        #     executor=executor,
        #     config=config,
        #     scope=scope,
        #     **kwargs
        # )
        self.endpoint = endpoint
        self._client = TableServiceClient(
            endpoint=endpoint,
            api_version=api_version,
            credential=credential,
            transport=transport,
            **kwargs
        )
        self._tables: Dict[str, TableClient] = {}

    def _get_table_client(self, tablename: str) -> TableClient:
        try:
            return self._tables[tablename]
        except KeyError:
            table_client = self._client.create_table_if_not_exists(tablename)
            self._tables[tablename] = table_client
            return table_client

    @overload
    def insert(self, table: str, *entities: Mapping[str, Any]) -> None:
        ...
    @overload
    def insert(self, *entities: DataModel) -> None:
        ...
    def insert(self, *args) -> None:
        if not args:
            return
        try:
            table_client = self._get_table_client(args[0].__table__)
            batch = [("create", e.model_dump(by_alias=True)) for e in args]
        except AttributeError:
            table_client = self._get_table_client(args[0])
            batch = [("create", e) for e in args[1:]]
        table_client.submit_transaction(batch)

    @overload
    def upsert(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
        ...
    @overload
    def upsert(self, *entities: DataModel, overwrite: bool = True) -> None:
        ...
    def upsert(self, *args, overwrite: bool = True) -> None:
        if not args:
            return
        mode = 'replace' if overwrite else 'merge'
        try:
            table_client = self._get_table_client(args[0].__table__)
            batch = [("upsert", e.model_dump(by_alias=True), {'mode': mode}) for e in args]
        except AttributeError:
            table_client = self._get_table_client(args[0])
            batch = [("upsert", e, {'mode': mode}) for e in args[1:]]
        table_client.submit_transaction(batch)

    @overload
    def update(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
        ...
    @overload
    def update(self, *entities: DataModel, overwrite: bool = True) -> None:
        ...
    def update(self, *args, overwrite: bool = True) -> None:
        if not args:
            return
        mode = 'replace' if overwrite else 'merge'
        try:
            table_client = self._get_table_client(args[0].__table__)
            batch = [("update", e.model_dump(by_alias=True), {'mode': mode}) for e in args]
        except AttributeError:
            table_client = self._get_table_client(args[0])
            batch = [("update", e, {'mode': mode}) for e in args[1:]]
        table_client.submit_transaction(batch)

    @overload
    def delete(self, table: str, *entities: Mapping[str, Any]) -> None:
        ...
    @overload
    def delete(self, *entities: DataModel) -> None:
        ...
    def delete(self, *args) -> None:
        if not args:
            return
        try:
            table_client = self._get_table_client(args[0].__table__)
            batch = [("delete", e.model_dump(by_alias=True)) for e in args]
        except AttributeError:
            table_client = self._get_table_client(args[0])
            batch = [("delete", e) for e in args[1:]]
        table_client.submit_transaction(batch)

    def list(self, table: Union[str, DataModel]) -> Generator[Mapping[str, Any], None, None]:
        try:
            table_client = self._get_table_client(table.__table__)
            for entity in table_client.list_entities():
                yield table(**entity)
        except AttributeError:
            table_client = self._get_table_client(table)
            yield from table_client.list_entities()

    @overload
    def query(self, table: str, partition: str, row: str, /) -> Generator[Mapping[str, Any], None, None]:
        ...
    @overload
    def query(self, table: str, *, query: str, parameters: Optional[Dict[str, Any]] = None) -> Generator[Mapping[str, Any], None, None]:
        ...
    @overload
    def query(self, table: Type[DataModel], partition: str, row: str, /) -> Generator[DataModel, None, None]:
        ...
    @overload
    def query(self, table: Type[DataModel], *, query: str, parameters: Optional[Dict[str, Any]] = None) -> Generator[Mapping[str, Any], None, None]:
        ...
    def query(self, table: Union[str, DataModel], *args, **kwargs) -> Generator[Mapping[str, Any], None, None]:
        if args:
            pk, rk = args
            if pk and pk != '*' and rk and rk != '*':
                try:
                    table_client = self._get_table_client(table.__table__)
                    entity = table_client.get_entity(pk, rk)
                    yield table(**entity)
                    return
                except AttributeError:
                    table_client = self._get_table_client(table)
                    yield table_client.get_entity(pk, rk)
                    return
            if pk and pk != '*':
                query = "PartitionKey eq @partition"
                parameters = {'partition': pk}
            elif rk and rk != '*':
                query = "RowKey eq @row"
                parameters = {'row': rk}
            else:
                raise ValueError("Both partition key and row key must be valid strings or '*'.")
        else:
            query = kwargs.pop('query')
            parameters = kwargs.pop('parameters', None) 
        try:
            table_client = self._get_table_client(table.__table__)
            for entity in table_client.query_entities(query, parameters=parameters):
                yield table(**entity)
        except AttributeError:
            table_client = self._get_table_client(table)
            yield from table_client.query_entities(query, parameters=parameters)


class ClientWithSettings(NamedTuple, Generic[ClientType, ClientSettingsType]):
    client: ClientType
    settings: ClientSettingsType


class CloudMachineClient:
    http_transport: HttpTransport

    def __init__(
            self,
            *,
            deployment: Optional[CloudMachineDeployment] = None,
            openai: Optional[Union[ClientSettings, str]] = None,
            data: Optional[Union[ClientSettings, str]] = None,
            messaging: Optional[Union[ClientSettings, str]] = None,
            storage: Optional[Union[ClientSettings, str]] = None,
            search: Optional[Union[ClientSettings, str]] = None,
            documentai: Optional[Union[ClientSettings, str]] = None,
            http_transport: Optional[HttpTransport] = None,
            event_listener: bool = True,
            client_options: Optional[Dict[str, Any]] = None,
            **kwargs
    ):
        self.http_transport = http_transport or self._build_transport()
        self._resources = global_resources
        self._client_options = client_options or {}
        self._settings: Dict[str, Optional[ClientSettings]] = {
            'openai': openai or (deployment.openai if deployment else None),
            'storage:blob': storage or (deployment.storage if deployment else None),
            'storage:table': data or (deployment.data if deployment else None),
            'servicebus': messaging or (deployment.messaging if deployment else None),
            'search': search or (deployment.search if deployment else None),
            'documentai': documentai or (deployment.documentai if deployment else None),
        }
        self.deployment = deployment
        if event_listener: # We shouldn't poll till we know someone is listening.
            self._listener = EventListener(
                cloudmachine=self,
            )
            self._listener_thread = Thread(target=self._listener, daemon=True)
        else:
            self._listener = None
            self._listener_thread = None

        self._executor: Executor = ThreadPoolExecutor(max_workers=kwargs.get('max_workers', 10))
        self._clients: Dict[str, Tuple[SyncClient, ClientSettings]] = {}

    def _build_transport(self, **kwargs):
        # Check transport setting
        import requests
        from azure.core.pipeline.transport import RequestsTransport
        session = requests.Session()
        session.mount(
            'https://',
            requests.adapters.HTTPAdapter(
                kwargs.pop('pool_connections', 25),
                kwargs.pop('pool_maxsize', 25)
            )
        )
        return TransportWrapper(
            RequestsTransport(
                session=session,
                session_owner=False,
                **kwargs
            )
        )

    @overload
    def get_client(
            self,
            service: Literal['storage:blob'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[BlobServiceClient, StorageClientSettings[BlobServiceClient]]:
        ...
    @overload
    def get_client(
            self,
            service: Literal['storage:blob'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_setings: Literal[False] = False
    ) -> BlobServiceClient:
        ...
    @overload
    def get_client(
            self, 
            service: Literal['storage:blob:container'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_setings: Literal[False] = False
    ) -> ContainerClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['storage:table'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_setings: Literal[False] = False
    ) -> TableServiceClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['servicebus'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_setings: Literal[False] = False
    ) -> ServiceBusClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['openai'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> AzureOpenAI:
        ...
    @overload
    def get_client(
            self,
            service: Literal['openai'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[AzureOpenAI, OpenAiClientSettings[AzureOpenAI]]:
        ...
    @overload
    def get_client(
            self,
            service: Literal['openai:embeddings'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> Embeddings:
        ...
    @overload
    def get_client(
            self,
            service: Literal['openai:embeddings'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[Embeddings, OpenAiClientSettings[AzureOpenAI]]:
        ...
    @overload
    def get_client(
            self, 
            service: Literal['openai:chat'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> Chat:
        ...
    @overload
    def get_client(
            self, 
            service: Literal['openai:chat'],
            *,
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[Chat, OpenAiClientSettings[AzureOpenAI]]:
        ...
    @overload
    def get_client(
            self,
            service: Literal['documentai'],
            *,
            name: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> DocumentIntelligenceClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['search'],
            *,
            name: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> SearchIndexClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['search'],
            *,
            name: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[SearchIndexClient, SearchClientSettings[SearchIndexClient]]:
        ...
    @overload
    def get_client(
            self,
            service: Literal['search:index'],
            *,
            settings: Optional[ClientSettings] = None,
            name: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> SearchClient:
        ...
    @overload
    def get_client(
            self,
            service: Literal['search:index'],
            *,
            settings: Optional[ClientSettings] = None,
            name: Optional[str] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[SearchClient, SearchClientSettings[SearchClient]]:
        ...
    @overload
    def get_client(
            self,
            service: str,
            *,
            cls: Callable[[], ClientType],
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[True]
    ) -> ClientWithSettings[ClientType, ClientSettings[ClientType]]:
        ...
    @overload
    def get_client(
            self,
            service: str,
            *,
            cls: Callable[[], ClientType],
            name: str = CloudmachineDefault,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: Literal[False] = False
    ) -> ClientType:
        ...
    def get_client(
            self,
            service: str,
            *,
            name: str = CloudmachineDefault,
            cls: Optional[Callable[..., ClientType]] = None,
            api_version: Optional[str] = None,
            client_options: Optional[Dict[str, Any]] = None,
            transport: Optional[TransportInputTypes] = None,
            credential: Optional[CredentialInputTypes] = None,
            with_settings: bool = False
    ) -> Union[SyncClient, Tuple[SyncClient, ClientSettings]]:
        client_options = client_options or {}
        resource_split = service.lower().split(":", 1)
        sub_resource = None
        client_key = service
        if resource_split[0] == 'openai':
            service = resource_split[0]
            try:
                # Whether to return an "embeddings" or "chat" client.
                sub_resource = resource_split[1]
            except IndexError:
                pass
        if name and name is not CloudmachineDefault:
            client_key = f"{name}:{client_key}"
        try:
            existing, settings = self._clients[client_key]
            if ((not cls or (settings.cls() == cls)) and
                (not api_version or (settings.api_version() == api_version)) and
                (not client_options or (settings.client_options() == client_options))):
                if with_settings:
                    return ClientWithSettings(existing, settings.copy())
                return existing
            self._clients[client_key].pop(name)
            existing.close()
        except KeyError:
            pass

        if name is not CloudmachineDefault or service not in self._settings:
            new_settings = global_resources.get(
                service,
                cls=cls,
                transport=transport,
                api_version=api_version,
                client_options=client_options)[name]
            new_settings.credential.set_value(credential)
        else:
            settings = self._settings[service]
            new_client_options = settings.client_options()
            new_client_options.update(client_options)
            new_settings = settings.copy(
                transport=transport,
                cls=cls,
                api_version=api_version,
                client_options=new_client_options,
                credential=credential
            )
        if service == "openai" and sub_resource:
            if sub_resource == "embeddings" and 'azure_deployment' not in client_options:
                new_client = new_settings.client(
                    client_options={'azure_deployment': new_settings.get('embeddings_deployment')}
                ).embeddings
            elif sub_resource == "chat" and 'azure_deployment' not in client_options:
                new_client = new_settings.client(
                    client_options={'azure_deployment': new_settings.get('chat_deployment')}
                ).chat
            else:
                raise ValueError(f"Unsupported openai resource: {sub_resource}")
        else:
            new_client = new_settings.client()
        self._clients[client_key] = (new_client, new_settings)
        if with_settings:
            return (new_client, new_settings)
        return new_client

    @property
    def storage(self) -> CloudMachineStorage:
        if self._listener_thread:  # TODO: Figure this out - should only start if someone listening
            try:
                self._listener_thread.start()
            except RuntimeError:
                pass
        try:
            return self._clients["cm:storage:blob"][0]
        except KeyError:
            settings = self._settings['storage:blob']
            if settings is None:
                raise RuntimeError("CloudMachine storage resource has not been configured.")
            client = settings.client(
                cls=CloudMachineStorage,
                transport=self.http_transport,
                client_options={
                    'account_name': settings.name()
                }
            )
            self._clients["cm:storage:blob"] = (client, settings)
            return client

    @property
    def messaging(self) -> CloudMachineServiceBus:
        try:
            return self._clients["cm:servicebus"][0]
        except KeyError:
            settings = self._settings['servicebus']
            if settings is None:
                raise RuntimeError("CloudMachine messaging resource has not been configured.")
            client = settings.client(
                cls=CloudMachineServiceBus,
                transport=self.http_transport,
            )
            self._clients["cm:servicebus"] = (client, settings)
            return client

    @property
    def data(self) -> CloudMachineTableData:
        try:
            return self._clients["cm:storage:table"][0]
        except KeyError:
            settings = self._settings['storage:table']
            if settings is None:
                raise RuntimeError("CloudMachine data resource has not been configured.")
            client = settings.client(
                cls=CloudMachineTableData,
                transport=self.http_transport,
            )
            self._clients["cm:storage:table"] = (client, settings)
            return client

    @property
    def document_index(self) -> CloudMachineDocumentIndex:
        try:
            return self._clients["cm:documentindex"][0]
        except KeyError:
            search=self._settings['search']
            if search is None:
                raise RuntimeError("CloudMachine search resource has not been configured.")
            openai=self._settings['openai']
            # documentai=self._settings['documentai'],
            new_client = CloudMachineDocumentIndex(
                search=search,
                openai=openai,
            )
            self._clients["cm:documentindex"] = (new_client, self._settings['search'])
            return new_client

    def close(self):
        self._listener.close()
        if self._listener_thread.is_alive():
            self._listener_thread.join()
        for service in self._clients:
            for client in self._clients[service]:
                self._clients[service][client].close()
        self.http_transport.close()
