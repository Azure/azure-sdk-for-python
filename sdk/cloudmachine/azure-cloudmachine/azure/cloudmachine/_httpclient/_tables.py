# # -------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for
# # license information.
# # --------------------------------------------------------------------------

# import os
# from urllib.parse import quote
# from typing import IO, Any, Dict, Generator, Literal, Mapping, Optional, Protocol, Type, Union, overload

# from azure.core import PipelineClient
# from azure.core.pipeline.transport import HttpTransport
# from azure.identity import DefaultAzureCredential
# from azure.core.rest import HttpRequest, HttpResponse
# from azure.core.tracing.decorator import distributed_trace
# from azure.core.utils import case_insensitive_dict

# from ._config import CloudMachinePipelineConfig
# from ._auth_policy import BearerTokenChallengePolicy, TOKEN_AUTH_SCOPES
# from ._api_versions import DEFAULT_API_VERSIONS


# class DataModel(Protocol):
#     def __init__(self, **kwargs) -> None:
#         ...

#     @property
#     def __table__(self) -> str:
#         ...
    
#     def model_dump(self, *, by_alias: bool = False, **kwargs) -> Dict[str, Any]:
#         ...


# class CloudMachineStorageTables:
#     _id: Literal["StorageTables"] = "StorageTables"

#     def __init__(
#             self,
#             *,
#             transport: Optional[HttpTransport] = None,
#             name: Optional[str] = None,
#             **kwargs
#     ):
#         if name:
#             name = name.upper()
#             endpoint = os.environ[f'AZURE_STORAGE_{name}_TABLE_ENDPOINT']
#         else:
#             endpoint = os.environ['AZURE_STORAGE_TABLE_ENDPOINT']

#         self._endpoint = endpoint.strip('/')
#         auth_policy = BearerTokenChallengePolicy(
#             DefaultAzureCredential(),
#             TOKEN_AUTH_SCOPES[self._id]
#         )
#         self._config = CloudMachinePipelineConfig(
#             api_version=kwargs.pop('api_version', DEFAULT_API_VERSIONS[self._id]),
#             authentication_policy=auth_policy,
#             transport=transport,
#             **kwargs
#         )
#         self._client = PipelineClient(
#             base_url=endpoint,
#             pipeline=self._config.pipeline,
#         )
#         self._tables: Dict[str, PipelineClient] = {}

#     def _get_table_client(self, tablename: str) -> PipelineClient:
#         try:
#             return self._tables[tablename]
#         except KeyError:
#             self._create_table(tablename)
#             table_url = self._endpoint + f"/{quote(tablename)}" 
#             self._tables[tablename] = PipelineClient(
#                 base_url=table_url,
#                 pipeline=self._config.pipeline,
#             )
#             return self._tables[tablename]

#     def get_client(self, **kwargs) -> 'azure.data.tables.TableServiceClient':
#         try:
#             from azure.data.tables import TableServiceClient
#         except ImportError as e:
#             raise ImportError("Please install azure-data-tables SDK to use SDK client.") from e
#         return TableServiceClient(
#             endpoint=self._endpoint,
#             api_version=self._config.api_version,
#             pipeline=self._config.pipeline,
#             **kwargs
#         )

#     @distributed_trace
#     def _create_table(self, tablename: str) -> None:
#         body = {'TableName': tablename}
#         request = build_table_create_request(
#             json=body
#         )
#         response = self._client.send_request(request)
#         print("RESPONSE", response.status_code)
#         response.raise_for_status()

#     @overload
#     def insert(self, table: str, *entities: Mapping[str, Any]) -> None:
#         ...
#     @overload
#     def insert(self, *entities: DataModel) -> None:
#         ...
#     @distributed_trace
#     def insert(self, *args) -> None:
#         if not args:
#             return
#         try:
#             table_client = self._get_table_client(args[0].__table__)
#             batch = [("create", e.model_dump(by_alias=True)) for e in args]
#         except AttributeError:
#             table_client = self._get_table_client(args[0])
#             batch = [("create", e) for e in args[1:]]
#         table_client.submit_transaction(batch)

#     @overload
#     def upsert(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
#         ...
#     @overload
#     def upsert(self, *entities: DataModel, overwrite: bool = True) -> None:
#         ...
#     @distributed_trace
#     def upsert(self, *args, overwrite: bool = True) -> None:
#         if not args:
#             return
#         mode = 'replace' if overwrite else 'merge'
#         try:
#             table_client = self._get_table_client(args[0].__table__)
#             batch = [("upsert", e.model_dump(by_alias=True), {'mode': mode}) for e in args]
#             print(batch)
#         except AttributeError:
#             table_client = self._get_table_client(args[0])
#             batch = [("upsert", e, {'mode': mode}) for e in args[1:]]
#         table_client.submit_transaction(batch)

#     @overload
#     def update(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
#         ...
#     @overload
#     def update(self, *entities: DataModel, overwrite: bool = True) -> None:
#         ...
#     @distributed_trace
#     def update(self, *args, overwrite: bool = True) -> None:
#         if not args:
#             return
#         mode = 'replace' if overwrite else 'merge'
#         try:
#             table_client = self._get_table_client(args[0].__table__)
#             batch = [("update", e.model_dump(by_alias=True), {'mode': mode}) for e in args]
#         except AttributeError:
#             table_client = self._get_table_client(args[0])
#             batch = [("update", e, {'mode': mode}) for e in args[1:]]
#         table_client.submit_transaction(batch)

#     @overload
#     def delete(self, table: str, *entities: Mapping[str, Any]) -> None:
#         ...
#     @overload
#     def delete(self, *entities: DataModel) -> None:
#         ...
#     @distributed_trace
#     def delete(self, *args) -> None:
#         if not args:
#             return
#         try:
#             table_client = self._get_table_client(args[0].__table__)
#             batch = [("delete", e.model_dump(by_alias=True)) for e in args]
#         except AttributeError:
#             table_client = self._get_table_client(args[0])
#             batch = [("delete", e) for e in args[1:]]
#         table_client.submit_transaction(batch)

#     @distributed_trace
#     def list(self, table: Union[str, DataModel]) -> Generator[Mapping[str, Any], None, None]:
#         try:
#             table_client = self._get_table_client(table.__table__)
#             for entity in table_client.list_entities():
#                 yield table(**entity)
#         except AttributeError:
#             table_client = self._get_table_client(table)
#             for entity in table_client.list_entities():
#                 yield entity

#     @overload
#     def query(self, table: str, partition: str, row: str, /) -> Generator[Mapping[str, Any], None, None]:
#         ...
#     @overload
#     def query(self, table: str, *, query: str, parameters: Optional[Dict[str, Any]] = None) -> Generator[Mapping[str, Any], None, None]:
#         ...
#     @overload
#     def query(self, table: Type[DataModel], partition: str, row: str, /) -> Generator[DataModel, None, None]:
#         ...
#     @overload
#     def query(self, table: Type[DataModel], *, query: str, parameters: Optional[Dict[str, Any]] = None) -> Generator[Mapping[str, Any], None, None]:
#         ...
#     @distributed_trace
#     def query(self, table: Union[str, DataModel], *args, **kwargs) -> Generator[Mapping[str, Any], None, None]:
#         if args:
#             pk, rk = args
#             if pk and pk != '*' and rk and rk != '*':
#                 try:
#                     table_client = self._get_table_client(table.__table__)
#                     entity = table_client.get_entity(pk, rk)
#                     yield table(**entity)
#                     return
#                 except AttributeError:
#                     table_client = self._get_table_client(table)
#                     yield table_client.get_entity(pk, rk)
#                     return
#             if pk and pk != '*':
#                 query = "PartitionKey eq @partition"
#                 parameters = {'partition': pk}
#             elif rk and rk != '*':
#                 query = "RowKey eq @row"
#                 parameters = {'row': rk}
#             else:
#                 raise ValueError("Both partition key and row key must be valid strings or '*'.")
#         else:
#              query = kwargs.pop('query')
#              parameters = kwargs.pop('parameters', None) 
#         try:
#             table_client = self._get_table_client(table.__table__)
#             for entity in table_client.query_entities(query, parameters=parameters):
#                 yield table(**entity)
#         except AttributeError:
#             table_client = self._get_table_client(table)
#             for entity in table_client.query_entities(query, parameters=parameters):
#                 yield entity



# ##### Generated request builders #####

# def build_table_create_request(
#     *,
#     json: Mapping[str, Any],
#     format: Optional[str] = None,
#     response_preference: Optional[str] = None,
#     **kwargs: Any
# ) -> HttpRequest:
#     _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
#     _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

#     data_service_version: Literal["3.0"] = kwargs.pop("data_service_version", _headers.pop("DataServiceVersion", "3.0"))
#     content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
#     version: Literal["2019-02-02"] = kwargs.pop("version", _headers.pop("x-ms-version", "2019-02-02"))
#     accept = _headers.pop("Accept", "application/json;odata=minimalmetadata")

#     # Construct URL
#     _url = "/Tables"
#     # Construct parameters
#     if format is not None:
#         _params["$format"] = str(format)
#     # Construct headers
#     _headers["x-ms-version"] = str(version)
#     _headers["DataServiceVersion"] = str(data_service_version)
#     if response_preference is not None:
#         _headers["Prefer"] = str(response_preference)
#     if content_type is not None:
#         _headers["Content-Type"] = str(content_type)
#     _headers["Accept"] = str(accept)
#     return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, json=json, **kwargs)


# def build_table_insert_entity_request(
#     table: str,
#     *,
#     timeout: Optional[int] = None,
#     format: Optional[str] = None,
#     response_preference: Optional[str] = None,
#     json: Optional[Dict[str, Any]] = None,
#     **kwargs: Any
# ) -> HttpRequest:
#     _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
#     _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

#     data_service_version: Literal["3.0"] = kwargs.pop("data_service_version", _headers.pop("DataServiceVersion", "3.0"))
#     content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
#     version: Literal["2019-02-02"] = kwargs.pop("version", _headers.pop("x-ms-version", "2019-02-02"))
#     accept = _headers.pop("Accept", "application/json;odata=minimalmetadata")

#     # Construct URL
#     _url = "/{table}"
#     path_format_arguments = {
#         "table": _SERIALIZER.url("table", table, "str"),
#     }

#     _url: str = _url.format(**path_format_arguments)  # type: ignore

#     # Construct parameters
#     if timeout is not None:
#         _params["timeout"] = _SERIALIZER.query("timeout", timeout, "int", minimum=0)
#     if format is not None:
#         _params["$format"] = _SERIALIZER.query("format", format, "str")

#     # Construct headers
#     _headers["x-ms-version"] = _SERIALIZER.header("version", version, "str")
#     _headers["DataServiceVersion"] = _SERIALIZER.header("data_service_version", data_service_version, "str")
#     if response_preference is not None:
#         _headers["Prefer"] = _SERIALIZER.header("response_preference", response_preference, "str")
#     if content_type is not None:
#         _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
#     _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

#     return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, json=json, **kwargs)

