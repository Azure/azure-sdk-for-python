# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import IO, Any, Dict, Generator, Generic, Literal, Mapping, Optional, Protocol, Type, TypeVar, Union, overload
from typing_extensions import Self
from threading import Thread
from concurrent.futures import Executor, ThreadPoolExecutor

from dotenv import load_dotenv, dotenv_values

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo
from azure.core.pipeline.transport import HttpTransport
from azure.data.tables import TableServiceClient, TableClient
from azure.identity import DefaultAzureCredential

from .resources._resources import Resources, resources as global_resources
from .resources._client_settings import ClientSettings, SyncClient
from .provisioning._deployment import azd_env_name, CloudMachineDeployment
from ._httpclient._eventlistener import EventListener, cloudmachine_events
from ._httpclient import TransportWrapper
from ._httpclient._servicebus import CloudMachineServiceBus
from ._httpclient._config import CloudMachinePipelineConfig
from ._httpclient._storage import CloudMachineStorage
from ._httpclient._base import CloudMachineClientlet

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = 'openai.AzureOpenAI'


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
    _id: Literal['Table'] = 'Table'

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
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            transport=transport,
            api_version=api_version,
            executor=executor,
            config=config,
            scope=scope,
            **kwargs
        )
        self._client = TableServiceClient(
            endpoint=self._endpoint,
            api_version=self._config.api_version,
            credential=self._credential,
            transport=self._config.transport,
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

    def get_client(self) -> TableServiceClient:
        return self._client

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


class CloudMachineClient:

    def __init__(
            self,
            *,
            resources: Optional[Resources] = None,
            deployment: Optional[CloudMachineDeployment] = None,
            http_transport: Optional[HttpTransport] = None,
            event_listener: bool = True,
            **kwargs
    ):
        self._http_transport = http_transport or self._build_transport(**kwargs)
        self._wrapped_transport = TransportWrapper(self._http_transport)
        if event_listener: # We shouldn't poll till we know someone is listening.
            self._listener = EventListener(
                cloudmachine=self,
                transport=self._wrapped_transport
            )
            self._listener_thread = Thread(target=self._listener, daemon=True)
        else:
            self._listener = None
            self._listener_thread = None

        self._executor: Executor = ThreadPoolExecutor(max_workers=kwargs.get('max_workers'))
        self._resources = resources or global_resources

    def _build_transport(self, **kwargs):
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
        return RequestsTransport(
            session=session,
            session_owner=False,
            **kwargs
        )

    def storage(self, name: Optional[str] = None) -> ClientSettings[CloudMachineStorage]:
        if self._listener_thread:
            try:
                self._listener_thread.start()
            except RuntimeError:
                pass
        return self._resources.get(
            'blobstorage',
            transport=self._http_transport,
            cls=CloudMachineStorage,
            client_options={'executor': self._executor}
        )[name or 'CLOUDMACHINE']

    def messaging(self, name: Optional[str] = None) -> ClientSettings[CloudMachineServiceBus]:
        return self._resources.get(
            'servicebus',
            transport=self._http_transport,
            cls=CloudMachineStorage,
            client_options={'executor': self._executor}
        )[name or 'CLOUDMACHINE']

    def data(self, name: Optional[str] = None) -> ClientSettings[CloudMachineTableData]:
        return self._resources.get(
            'servicebus',
            transport=self._http_transport,
            cls=CloudMachineStorage,
            client_options={'executor': self._executor}
        )[name or 'CLOUDMACHINE']

    def vault(self, name: Optional[str] = None) -> ClientSettings:
        return self._resources.get(
            'keyvault',
            transport=self._http_transport,
            #cls=CloudMachineKeyVault,
            client_options={'executor': self._executor}
        )[name or 'CLOUDMACHINE']

    def ai(self, name: Optional[str] = None) -> ClientSettings[AzureOpenAI]:
        return self._resources.get(
            'openai',
            transport=self._http_transport,
            cls=CloudMachineStorage,
            client_options={'executor': self._executor}
        )[name or 'CLOUDMACHINE']

    def close(self):
        self._listener.close()
        for storage_client in self._storage.values():
            storage_client.close()
        for queue_client in self._messaging.values():
            queue_client.close()
        for table_client in self._data.values():
            table_client.close()
        if self._listener_thread.is_alive():
            self._listener_thread.join()
        self._http_transport.close()
