#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Create, read, update and delete and execute scripts in the Azure Cosmos DB SQL API service.
"""

import six
from azure.cosmos.cosmos_client_connection import CosmosClientConnection
from .partition_key import NonePartitionKeyValue
from.query_iterable import QueryIterable
from typing import (
    Any,
    List,
    Dict,
    Union,
)


class ScriptType:
    StoredProcedure = "sprocs"
    Trigger = "triggers"
    UserDefinedFunction = "udfs"


class Scripts:

    def __init__(self, client_connection, container_link, is_system_key):
        # type: (CosmosClientConnection, str, bool) -> None
        self.client_connection = client_connection
        self.container_link = container_link
        self.is_system_key = is_system_key

    def _get_resource_link(self, script_or_id, type):
        # type: (Union[Dict[str, Any], str], str) -> str
        if isinstance(script_or_id, six.string_types):
            return u"{}/{}/{}".format(self.container_link, type, script_or_id)
        return script_or_id["_self"]

    def list_stored_procedures(
            self,
            max_item_count=None,
            feed_options=None
    ):
        # type: (int, Dict[str, Any]) -> QueryIterable
        """ List all stored procedures in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of stored procedures (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadStoredProcedures(
            collection_link=self.container_link,
            options=feed_options
        )

    def query_stored_procedures(
            self,
            query,
            parameters=None,
            max_item_count=None,
            feed_options=None
    ):
        # type: (str, List, int, Dict[str, Any]) -> QueryIterable
        """Return all stored procedures matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of stored procedures (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryStoredProcedures(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=feed_options,
        )

    def get_stored_procedure(
            self,
            sproc,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        """
        Get the stored procedure identified by `id`.

        :param sproc: The ID (name) or dict representing stored procedure to retrieve.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the retrieved stored procedure.
        :raise `HTTPFailure`: If the given stored procedure couldn't be retrieved.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReadStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            options=request_options
        )

    def create_stored_procedure(
            self,
            body,
            request_options=None
    ):
        # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Create a stored procedure in the container.

        :param body: A dict-like object representing the sproc to create.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the new stored procedure.
        :raise `HTTPFailure`: If the given stored procedure couldn't be created.

        To replace an existing sproc, use the :func:`Container.scripts.replace_stored_procedure` method.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.CreateStoredProcedure(
            collection_link=self.container_link,
            sproc=body,
            options=request_options
        )

    def replace_stored_procedure(
            self,
            sproc,
            body,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified stored procedure if it exists in the container.

        :param sproc: The ID (name) or dict representing stored procedure to be replaced.
        :param body: A dict-like object representing the sproc to replace.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the stored procedure after replace went through.
        :raise `HTTPFailure`: If the replace failed or the stored procedure with given id does not exist.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReplaceStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            sproc=body,
            options=request_options
        )

    def delete_stored_procedure(
            self,
            sproc,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> None
        """ Delete the specified stored procedure from the container.

        :param sproc: The ID (name) or dict representing stored procedure to be deleted.
        :param request_options: Dictionary of additional properties to be used for the request.
        :raises `HTTPFailure`: The sproc wasn't deleted successfully. If the sproc does not exist in the container, a `404` error is returned.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        self.client_connection.DeleteStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            options=request_options
        )

    def execute_stored_procedure(
            self,
            sproc,
            partition_key=None,
            params=None,
            enable_script_logging=None,
            request_options = None
    ):
        # type: (Union[str, Dict[str, Any]], str, List[Any], bool, Dict[str, Any]) -> Any
        """ execute the specified stored procedure.

        :param sproc: The ID (name) or dict representing stored procedure to be executed.
        :param params: List of parameters to be passed to the stored procedure to be executed.
        :param enable_script_logging: Enables or disables script logging for the current request.
        :param partition_key: Specifies the partition key to indicate which partition the sproc should execute on.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: result of the executed stored procedure for the given parameters.
        :raise `HTTPFailure`: If the stored procedure execution failed or if the stored procedure with given id does not exists in the container.

        """

        if not request_options:
            request_options = {} # type: Dict[str, Any]
        if partition_key is not None:
            request_options["partitionKey"] = (CosmosClientConnection._return_undefined_or_empty_partition_key(self.is_system_key)
                                               if partition_key == NonePartitionKeyValue else partition_key)
        if enable_script_logging is not None:
            request_options["enableScriptLogging"] = enable_script_logging

        return self.client_connection.ExecuteStoredProcedure(
            sproc_link=self._get_resource_link(sproc, ScriptType.StoredProcedure),
            params=params,
            options=request_options
        )

    def list_triggers(
            self,
            max_item_count=None,
            feed_options=None
    ):
        # type: (int, Dict[str, Any]) -> QueryIterable
        """ List all triggers in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of triggers (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadTriggers(
            collection_link=self.container_link,
            options=feed_options
        )

    def query_triggers(
            self,
            query,
            parameters=None,
            max_item_count=None,
            feed_options=None
    ):
        # type: (str, List, int, Dict[str, Any]) -> QueryIterable
        """Return all triggers matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of triggers (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryTriggers(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=feed_options,
        )

    def get_trigger(
            self,
            trigger,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        """
        Get the trigger identified by `id`.

        :param trigger: The ID (name) or dict representing trigger to retrieve.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the retrieved trigger.
        :raise `HTTPFailure`: If the given trigger couldn't be retrieved.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReadTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger),
            options=request_options
        )

    def create_trigger(
            self,
            body,
            request_options=None
    ):
        # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Create a trigger in the container.

        :param body: A dict-like object representing the trigger to create.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the new trigger.
        :raise `HTTPFailure`: If the given trigger couldn't be created.

        To replace an existing trigger, use the :func:`Container.scripts.replace_trigger` method.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.CreateTrigger(
            collection_link=self.container_link,
            trigger=body,
            options=request_options
        )

    def replace_trigger(
            self,
            trigger,
            body,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified tigger if it exists in the container.

        :param trigger: The ID (name) or dict representing trigger to be replaced.
        :param body: A dict-like object representing the trigger to replace.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the trigger after replace went through.
        :raise `HTTPFailure`: If the replace failed or the trigger with given id does not exist.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReplaceTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger),
            trigger=body,
            options=request_options
        )

    def delete_trigger(
            self,
            trigger,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> None
        """ Delete the specified trigger from the container.

        :param trigger: The ID (name) or dict representing trigger to be deleted.
        :param request_options: Dictionary of additional properties to be used for the request.
        :raises `HTTPFailure`: The trigger wasn't deleted successfully. If the trigger does not exist in the container, a `404` error is returned.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        self.client_connection.DeleteTrigger(
            trigger_link=self._get_resource_link(trigger, ScriptType.Trigger),
            options=request_options
        )


    def list_user_defined_functions(
            self,
            max_item_count=None,
            feed_options=None
    ):
        # type: (int, Dict[str, Any]) -> QueryIterable
        """ List all user defined functions in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of user defined functions (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUserDefinedFunctions(
            collection_link=self.container_link,
            options=feed_options,
        )

    def query_user_defined_functions(
            self,
            query,
            parameters=None,
            max_item_count=None,
            feed_options=None
    ):
        # type: (str, List, int, Dict[str, Any]) -> QueryIterable
        """Return all user defined functions matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of user defined functions (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryUserDefinedFunctions(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=feed_options,
        )

    def get_user_defined_function(
            self,
            udf,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        """
        Get the stored procedure identified by `id`.

        :param udf: The ID (name) or dict representing udf to retrieve.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the retrieved user defined function.
        :raise `HTTPFailure`: If the given user defined function couldn't be retrieved.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReadUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction),
            options=request_options
        )

    def create_user_defined_function(
            self,
            body,
            request_options=None
    ):
        # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Create a user defined function in the container.

        :param body: A dict-like object representing the udf to create.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the new user defined function.
        :raise `HTTPFailure`: If the given user defined function couldn't be created.

        To replace an existing udf, use the :func:`Container.scripts.replace_user_defined_function` method.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.CreateUserDefinedFunction(
            collection_link=self.container_link,
            udf=body,
            options=request_options
        )

    def replace_user_defined_function(
            self,
            udf,
            body,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified user defined function if it exists in the container.

        :param udf: The ID (name) or dict representing udf to be replaced.
        :param body: A dict-like object representing the udf to replace.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the user defined function after replace went through.
        :raise `HTTPFailure`: If the replace failed or the user defined function with given id does not exist.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        return self.client_connection.ReplaceUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction),
            udf=body,
            options=request_options
        )

    def delete_user_defined_function(
            self,
            udf,
            request_options=None
    ):
        # type: (Union[str, Dict[str, Any]], Dict[str, Any]) -> None
        """ Delete the specified user defined function from the container.

        :param udf: The ID (name) or dict representing udf to be deleted.
        :param request_options: Dictionary of additional properties to be used for the request.
        :raises `HTTPFailure`: The udf wasn't deleted successfully. If the udf does not exist in the container, a `404` error is returned.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        self.client_connection.DeleteUserDefinedFunction(
            udf_link=self._get_resource_link(udf, ScriptType.UserDefinedFunction),
            options=request_options
        )
