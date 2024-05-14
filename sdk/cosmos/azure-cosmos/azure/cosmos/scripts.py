# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Create, read, update and delete and execute scripts in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Dict, List, Mapping, Union, Optional, Type, Sequence

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options
from .partition_key import NonePartitionKeyValue, _return_undefined_or_empty_partition_key

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

PartitionKeyType = Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]]  # pylint: disable=line-too-long


class ScriptType:
    StoredProcedure = "sprocs"
    Trigger = "triggers"
    UserDefinedFunction = "udfs"


class ScriptsProxy:
    """An interface to interact with stored procedures.

    This class should not be instantiated directly. Instead, use the
    :func:`ContainerProxy.scripts` attribute.
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        container_link: str,
        is_system_key: bool
    ) -> None:
        self.client_connection = client_connection
        self.container_link = container_link
        self.is_system_key = is_system_key

    def _get_resource_link(self, script_or_id: Union[str, Mapping[str, Any]], typ: str) -> str:
        if isinstance(script_or_id, str):
            return "{}/{}/{}".format(self.container_link, typ, script_or_id)
        return script_or_id["_self"]

    @distributed_trace
    def list_stored_procedures(
        self,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List all stored procedures in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of stored procedures (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadStoredProcedures(
            collection_link=self.container_link, options=feed_options, **kwargs
        )

    @distributed_trace
    def query_stored_procedures(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return all stored procedures matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, Any]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of stored procedures (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        return self.client_connection.QueryStoredProcedures(
            collection_link=self.container_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )

    @distributed_trace
    def get_stored_procedure(self, sproc: Union[str, Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Get the stored procedure identified by `id`.

        :param sproc: The ID (name) or dict representing stored procedure to retrieve.
        :type sproc: Union[str, Dict[str, Any]]
        :returns: A dict representing the retrieved stored procedure.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given stored procedure couldn't be retrieved.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReadStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure), options=request_options, **kwargs
        )

    @distributed_trace
    def create_stored_procedure(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create a new stored procedure in the container.

        To replace an existing sproc, use the :func:`Container.scripts.replace_stored_procedure` method.

        :param Dict[str, Any] body: A dict-like object representing the sproc to create.
        :returns: A dict representing the new stored procedure.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given stored procedure couldn't be created.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.CreateStoredProcedure(
            collection_link=self.container_link, sproc=body, options=request_options, **kwargs
        )

    @distributed_trace
    def replace_stored_procedure(
        self,
        sproc: Union[str, Mapping[str, Any]],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replace a specified stored procedure in the container.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be replaced.
        :type sproc: Union[str, Dict[str, Any]]
        :param Dict[str, Any] body: A dict-like object representing the sproc to replace.
        :returns: A dict representing the stored procedure after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace operation failed or the stored
            procedure with given id does not exist.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        return self.client_connection.ReplaceStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            sproc=body,
            options=request_options,
            **kwargs
        )

    @distributed_trace
    def delete_stored_procedure(self, sproc: Union[str, Mapping[str, Any]], **kwargs: Any) -> None:
        """Delete a specified stored procedure from the container.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be deleted.
        :type sproc: Union[str, Dict[str, Any]]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The sproc wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The sproc does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        self.client_connection.DeleteStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure), options=request_options, **kwargs
        )

    @distributed_trace
    def execute_stored_procedure(
        self,
        sproc: Union[str, Mapping[str, Any]],
        partition_key: Optional[PartitionKeyType] = None,
        params: Optional[List[Dict[str, Any]]] = None,
        enable_script_logging: Optional[bool] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a specified stored procedure.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be executed.
        :type sproc: Union[str, Dict[str, Any]]
        :param partition_key: Specifies the partition key to indicate which partition the sproc should execute on.
        :type partition_key: Union[str, int, float, bool]
        :param params: List of parameters to be passed to the stored procedure to be executed.
        :type params: List[Dict[str, Any]]
        :param bool enable_script_logging: Enables or disables script logging for the current request.
        :returns: Result of the executed stored procedure for the given parameters.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the stored procedure execution failed
            or if the stored procedure with given id does not exist in the container.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        if partition_key is not None:
            request_options["partitionKey"] = (
                _return_undefined_or_empty_partition_key(self.is_system_key)
                if partition_key == NonePartitionKeyValue
                else partition_key
            )
        if enable_script_logging is not None:
            request_options["enableScriptLogging"] = enable_script_logging

        return self.client_connection.ExecuteStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            params=params,
            options=request_options,
            **kwargs
        )

    @distributed_trace
    def list_triggers(self, max_item_count: Optional[int] = None, **kwargs: Any) -> ItemPaged[Dict[str, Any]]:
        """List all triggers in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of triggers (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadTriggers(
            collection_link=self.container_link, options=feed_options, **kwargs
        )

    @distributed_trace
    def query_triggers(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return all triggers matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, Any]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of triggers (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryTriggers(
            collection_link=self.container_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )

    @distributed_trace
    def get_trigger(self, trigger: Union[str, Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Get a trigger identified by `id`.

        :param trigger: The ID (name) or dict representing trigger to retrieve.
        :type trigger: Union[str, Dict[str, Any]]
        :returns: A dict representing the retrieved trigger.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given trigger couldn't be retrieved.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReadTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger), options=request_options, **kwargs
        )

    @distributed_trace
    def create_trigger(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create a trigger in the container.

        To replace an existing trigger, use the :func:`ContainerProxy.scripts.replace_trigger` method.

        :param Dict[str, Any] body: A dict-like object representing the trigger to create.
        :returns: A dict representing the new trigger.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given trigger couldn't be created.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        return self.client_connection.CreateTrigger(
            collection_link=self.container_link, trigger=body, options=request_options, **kwargs
        )

    @distributed_trace
    def replace_trigger(
        self,
        trigger: Union[str, Mapping[str, Any]],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replace a specified trigger in the container.

        If the trigger does not already exist in the container, an exception is raised.

        :param trigger: The ID (name) or dict representing trigger to be replaced.
        :type trigger: Union[str, Dict[str, Any]]
        :param Dict[str, Any] body: A dict-like object representing the trigger to replace.
        :returns: A dict representing the trigger after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace operation failed or the trigger
            with given id does not exist.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReplaceTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger),
            trigger=body,
            options=request_options,
            **kwargs
        )

    @distributed_trace
    def delete_trigger(self, trigger: Union[str, Mapping[str, Any]], **kwargs: Any) -> None:
        """Delete a specified trigger from the container.

        If the trigger does not already exist in the container, an exception is raised.

        :param trigger: The ID (name) or dict representing trigger to be deleted.
        :type trigger: Union[str, Dict[str, Any]]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The trigger wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The trigger does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        self.client_connection.DeleteTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger), options=request_options, **kwargs
        )

    @distributed_trace
    def list_user_defined_functions(
        self,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List all the user-defined functions in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of user-defined functions (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUserDefinedFunctions(
            collection_link=self.container_link, options=feed_options, **kwargs
        )

    @distributed_trace
    def query_user_defined_functions(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return user-defined functions matching a given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, Any]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of user-defined functions (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryUserDefinedFunctions(
            collection_link=self.container_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )

    @distributed_trace
    def get_user_defined_function(self, udf: Union[str, Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Get a user-defined functions identified by `id`.

        :param udf: The ID (name) or dict representing udf to retrieve.
        :type udf: Union[str, Dict[str, Any]]
        :returns: A dict representing the retrieved user-defined function.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the user-defined function couldn't be retrieved.
        :rtype: Iterable[Dict[str, Any]]
        """
        request_options = build_options(kwargs)
        return self.client_connection.ReadUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction), options=request_options, **kwargs
        )

    @distributed_trace
    def create_user_defined_function(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create a user-defined function in the container.

        To replace an existing UDF, use the :func:`ContainerProxy.scripts.replace_user_defined_function` method.

        :param Dict[str, Any] body: A dict-like object representing the udf to create.
        :returns: A dict representing the new user-defined function.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the user-defined function couldn't be created.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        return self.client_connection.CreateUserDefinedFunction(
            collection_link=self.container_link, udf=body, options=request_options, **kwargs
        )

    @distributed_trace
    def replace_user_defined_function(
        self,
        udf: Union[str, Mapping[str, Any]],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replace a specified user-defined function in the container.

        If the UDF does not already exist in the container, an exception is raised.

        :param udf: The ID (name) or dict representing udf to be replaced.
        :type udf: Union[str, Dict[str, Any]]
        :param Dict[str, Any] body: A dict-like object representing the udf to replace.
        :returns: A dict representing the user-defined function after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace operation failed or the user-defined
            function with the given id does not exist.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        return self.client_connection.ReplaceUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction),
            udf=body,
            options=request_options,
            **kwargs
        )

    @distributed_trace
    def delete_user_defined_function(self, udf: Union[str, Mapping[str, Any]], **kwargs: Any) -> None:
        """Delete a specified user-defined function from the container.

        If the UDF does not already exist in the container, an exception is raised.

        :param udf: The ID (name) or dict representing udf to be deleted.
        :type udf: Union[str, Dict[str, Any]]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The udf wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The UDF does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        self.client_connection.DeleteUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction), options=request_options, **kwargs
        )
