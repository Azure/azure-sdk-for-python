# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import IO, Any, Dict, Generator, Mapping, Optional, Protocol, Type, Union, overload
from threading import Thread
from concurrent.futures import Executor

from dotenv import load_dotenv, dotenv_values

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.pipeline.transport import HttpTransport
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.data.tables import TableServiceClient, TableClient
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient

from .resources import azd_env_name
from ._eventlistener import EventListener


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
    return dotenv_values(os.path.join(azd_dir, env_name, ".env"))


class CloudMachineStorage:
    default_container_name: str = "default"
    
    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            name: Optional[str] = None,
            executor: Optional[Executor] = None,
            **kwargs
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_STORAGE_{name}_BLOB_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_STORAGE_BLOB_ENDPOINT']
        if f'AZURE_STORAGE_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_STORAGE_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_STORAGE_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = BlobServiceClient(
            account_url=endpoint,
            credential=credential,
            transport=transport,
            **kwargs
        )
        self._default_container = self._client.get_container_client(self.default_container_name)
        self._containers: Dict[str, ContainerClient] = {}

    def _get_container_client(self, container: Optional[str]) -> ContainerClient:
        if container:
            try:
                return self._containers[container]
            except KeyError:
                container_client = self._client.get_container_client(container)
                self._containers[container] = container_client
                return container_client
        return self._default_container

    def get_client(self) -> BlobServiceClient:
        return self._client

    def list(
            self,
            *,
            prefix: Optional[str] = None,
            container: Optional[str] = None
    ) -> Generator[str, None, None]:
        client = self._get_container_client(container)
        for blob in client.list_blobs(name_starts_with=prefix):
            yield blob.name

    def delete(self, name: str, *, container: Optional[str] = None) -> None:
        client = self._get_container_client(container)
        client.delete_blob(name)

    def upload(self, name: str, filedata: IO[bytes], *, container: Optional[str] = None) -> None:
        client = self._get_container_client(container)
        client.upload_blob(name, filedata, overwrite=True)

    def download(self, name: str, *, container: Optional[str] = None) -> Generator[bytes, None, None]:
        client = self._get_container_client(container)
        download = client.download_blob(name)
        for data in download.chunks():
            yield data
    
    def create_container(self, name: str) -> None:
        client = self._client.create_container(name)
        self._containers[name] = client

    def delete_container(self, name: str) -> None:
        if name.lower() == "default":
            raise ValueError("Default container cannot be deleted.")
        try:
            container = self._containers.pop(name)
            container.delete_container()
        except KeyError:
            self._client.delete_container(name)

    def close(self) -> None:
        self._client.close()


class CloudMachineMessaging:
    default_queue_name: str = "default"

    def __init__(
            self,
            *,
            name: Optional[str] = None,
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_SERVICE_BUS_{name}_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_SERVICE_BUS_ENDPOINT']
        if f'AZURE_SERVICE_BUS_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_SERVICE_BUS_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_SERVICE_BUS_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=endpoint,
            credential=credential,
        )
        #self._default_queue_sender = self._client.get_queue_sender(self.default_queue_name)
        #self._default_queue_receiver = 
        #self._containers: Dict[str, ContainerClient] = {}

    def get_client(self) -> ServiceBusClient:
        return self._client

    def close(self) -> None:
        self._client.close()


class DataModel(Protocol):
    def __init__(self, **kwargs) -> None:
        ...

    @property
    def __table__(self) -> str:
        ...
    
    def model_dump(self, *, by_alias: bool = False, **kwargs) -> Dict[str, Any]:
        ...
    

class CloudMachineTableData:
    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            name: Optional[str] = None,
            **kwargs
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_STORAGE_{name}_TABLE_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_STORAGE_TABLE_ENDPOINT']
        if f'AZURE_STORAGE_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_STORAGE_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_STORAGE_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = TableServiceClient(
            endpoint=endpoint,
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
            print(batch)
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
            for entity in table_client.list_entities():
                yield entity

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
            for entity in table_client.query_entities(query, parameters=parameters):
                yield entity


class CloudMachineClient:

    def __init__(
            self,
            *,
            http_transport: Optional[HttpTransport] = None,
            **kwargs
    ):
        self._http_transport = http_transport or self._build_transport(**kwargs)
        self._listener = EventListener()
        self._listener_thread = Thread(target=self._listener, daemon=True)
        self._storage: Dict[CloudMachineStorage] = {}
        self._messaging: Dict[CloudMachineMessaging] = {}
        self._data: Dict[CloudMachineTableData] = {}

    def _build_transport(self, **kwargs):
        import requests
        from azure.core.pipeline.transport import RequestsTransport
        session = requests.Session()
        session.mount(
            'https://',
            requests.adapters.HTTPAdapter(
                kwargs.pop('pool_connections', 10),
                kwargs.pop('pool_maxsize', 10)
            )
        )
        return RequestsTransport(
            session=session,
            session_owner=False,
            **kwargs
        )

    @property
    def storage(self):
        if not self._storage:
            self._listener_thread.start()
            self._storage['default'] = CloudMachineStorage(transport=self._http_transport)
        return self._storage['default']

    @property
    def messaging(self):
        if not self._messaging:
            self._messaging['default'] = CloudMachineMessaging()
        return self._messaging['default']

    @property
    def data(self):
        if not self._data:
            self._data['default'] = CloudMachineTableData(transport=self._http_transport)
        return self._data['default']

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
