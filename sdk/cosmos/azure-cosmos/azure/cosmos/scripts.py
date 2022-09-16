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

from typing import Any, List, Dict, Union, Iterable, Optional

from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from ._base import build_options
from .partition_key import NonePartitionKeyValue

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs


class ScriptType(object):
    StoredProcedure = "sprocs"
    Trigger = "triggers"
    UserDefinedFunction = "udfs"


class ScriptsProxy(object):
    """An interface to interact with stored procedures.

    This class should not be instantiated directly. Instead, use the
    :func:`ContainerProxy.scripts` attribute.
    """

    def __init__(self, client_connection, container_link, is_system_key):
        # type: (CosmosClientConnection, str, bool) -> None
        self.client_connection = client_connection
        self.container_link = container_link
        self.is_system_key = is_system_key

    def _get_resource_link(self, script_or_id, typ):
        # type: (Union[Dict[str, Any], str], str) -> str
        if isinstance(script_or_id, str):
            return u"{}/{}/{}".format(self.container_link, typ, script_or_id)
        return script_or_id["_self"]

    def list_stored_procedures(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
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

    def query_stored_procedures(self, query, parameters=None, max_item_count=None, **kwargs):
        # type: (str, Optional[List[str]], Optional[int], Any) -> Iterable[Dict[str, Any]]
        """Return all stored procedures matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of stored procedures (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryStoredProcedures(
            collection_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )

    def get_stored_procedure(self, sproc, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> Dict[str, Any]
        """Get the stored procedure identified by `id`.

        :param sproc: The ID (name) or dict representing stored procedure to retrieve.
        :returns: A dict representing the retrieved stored procedure.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given stored procedure couldn't be retrieved.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReadStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure), options=request_options, **kwargs
        )

    def create_stored_procedure(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> Dict[str, Any]
        """Create a new stored procedure in the container.

        To replace an existing sproc, use the :func:`Container.scripts.replace_stored_procedure` method.

        :param body: A dict-like object representing the sproc to create.
        :returns: A dict representing the new stored procedure.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given stored procedure couldn't be created.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.CreateStoredProcedure(
            collection_link=self.container_link, sproc=body, options=request_options, **kwargs
        )

    def replace_stored_procedure(self, sproc, body, **kwargs):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Any) -> Dict[str, Any]
        """Replace a specified stored procedure in the container.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be replaced.
        :param body: A dict-like object representing the sproc to replace.
        :returns: A dict representing the stored procedure after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace failed or the stored
            procedure with given id does not exist.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReplaceStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            sproc=body,
            options=request_options,
            **kwargs
        )

    def delete_stored_procedure(self, sproc, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> None
        """Delete a specified stored procedure from the container.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be deleted.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The sproc wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The sproc does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)

        self.client_connection.DeleteStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure), options=request_options, **kwargs
        )

    def execute_stored_procedure(
        self,
        sproc,  # type: Union[str, Dict[str, Any]]
        partition_key=None,  # type: Optional[str]
        params=None,  # type: Optional[List[Any]]
        enable_script_logging=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> Any
        """Execute a specified stored procedure.

        If the stored procedure does not already exist in the container, an exception is raised.

        :param sproc: The ID (name) or dict representing stored procedure to be executed.
        :param partition_key: Specifies the partition key to indicate which partition the sproc should execute on.
        :param params: List of parameters to be passed to the stored procedure to be executed.
        :param bool enable_script_logging: Enables or disables script logging for the current request.
        :returns: Result of the executed stored procedure for the given parameters.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the stored procedure execution failed
            or if the stored procedure with given id does not exists in the container.
        :rtype: dict[str, Any]
        """

        request_options = build_options(kwargs)
        if partition_key is not None:
            request_options["partitionKey"] = (
                CosmosClientConnection._return_undefined_or_empty_partition_key(self.is_system_key)
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

    def list_triggers(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
        """List all triggers in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of triggers (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadTriggers(
            collection_link=self.container_link, options=feed_options, **kwargs
        )

    def query_triggers(self, query, parameters=None, max_item_count=None, **kwargs):
        # type: (str, Optional[List[str]], Optional[int], Any) -> Iterable[Dict[str, Any]]
        """Return all triggers matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of triggers (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryTriggers(
            collection_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )

    def get_trigger(self, trigger, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> Dict[str, Any]
        """Get a trigger identified by `id`.

        :param trigger: The ID (name) or dict representing trigger to retrieve.
        :returns: A dict representing the retrieved trigger.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given trigger couldn't be retrieved.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReadTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger), options=request_options, **kwargs
        )

    def create_trigger(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> Dict[str, Any]
        """Create a trigger in the container.

        To replace an existing trigger, use the :func:`ContainerProxy.scripts.replace_trigger` method.

        :param body: A dict-like object representing the trigger to create.
        :returns: A dict representing the new trigger.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given trigger couldn't be created.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.CreateTrigger(
            collection_link=self.container_link, trigger=body, options=request_options, **kwargs
        )

    def replace_trigger(self, trigger, body, **kwargs):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Any) -> Dict[str, Any]
        """Replace a specified trigger in the container.

        If the trigger does not already exist in the container, an exception is raised.

        :param trigger: The ID (name) or dict representing trigger to be replaced.
        :param body: A dict-like object representing the trigger to replace.
        :returns: A dict representing the trigger after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace failed or the trigger with given
            id does not exist.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReplaceTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger),
            trigger=body,
            options=request_options,
            **kwargs
        )

    def delete_trigger(self, trigger, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> None
        """Delete a specified trigger from the container.

        If the trigger does not already exist in the container, an exception is raised.

        :param trigger: The ID (name) or dict representing trigger to be deleted.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The trigger wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The trigger does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)

        self.client_connection.DeleteTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger), options=request_options, **kwargs
        )

    def list_user_defined_functions(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
        """List all the user-defined functions in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of user-defined functions (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUserDefinedFunctions(
            collection_link=self.container_link, options=feed_options, **kwargs
        )

    def query_user_defined_functions(self, query, parameters=None, max_item_count=None, **kwargs):
        # type: (str, Optional[List[str]], Optional[int], Any) -> Iterable[Dict[str, Any]]
        """Return user-defined functions matching a given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An Iterable of user-defined functions (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryUserDefinedFunctions(
            collection_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )

    def get_user_defined_function(self, udf, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> Dict[str, Any]
        """Get a user-defined functions identified by `id`.

        :param udf: The ID (name) or dict representing udf to retrieve.
        :returns: A dict representing the retrieved user-defined function.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the user-defined function couldn't be retrieved.
        :rtype: Iterable[dict[str, Any]]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReadUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction), options=request_options, **kwargs
        )

    def create_user_defined_function(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> Dict[str, Any]
        """Create a user-defined function in the container.

        To replace an existing UDF, use the :func:`ContainerProxy.scripts.replace_user_defined_function` method.

        :param body: A dict-like object representing the udf to create.
        :returns: A dict representing the new user-defined function.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the user-defined function couldn't be created.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.CreateUserDefinedFunction(
            collection_link=self.container_link, udf=body, options=request_options, **kwargs
        )

    def replace_user_defined_function(self, udf, body, **kwargs):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Any) -> Dict[str, Any]
        """Replace a specified user-defined function in the container.

        If the UDF does not already exist in the container, an exception is raised.

        :param udf: The ID (name) or dict representing udf to be replaced.
        :param body: A dict-like object representing the udf to replace.
        :returns: A dict representing the user-defined function after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace failed or the user-defined function
            with the given id does not exist.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)

        return self.client_connection.ReplaceUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction),
            udf=body,
            options=request_options,
            **kwargs
        )

    def delete_user_defined_function(self, udf, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any) -> None
        """Delete a specified user-defined function from the container.

        If the UDF does not already exist in the container, an exception is raised.

        :param udf: The ID (name) or dict representing udf to be deleted.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The udf wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The UDF does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)

        self.client_connection.DeleteUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction), options=request_options, **kwargs
        )
