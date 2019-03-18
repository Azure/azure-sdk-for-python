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

from azure.cosmos.cosmos_client_connection import CosmosClientConnection


class ScriptType:
    StoredProcedure = "sprocs"
    Trigger = "triggers"
    UserDefinedFunction = "udfs"


class Scripts:

    def __init__(self, client_connection, container_link):
        # type: (CosmosClientConnection, Union[Container, str], str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.container_link = container_link

    def _get_resource_link(self, id, type):
        return "{}/{}/{}".format(self.container_link, type, id)

    def list_stored_procedures(self, max_item_count=None):
        # type: (int) -> QueryIterable
        """ List all stored procedures in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadStoredProcedures(
            collection_link=self.container_link,
            options=request_options
        )

    def query_stored_procedures(self, query, parameters=None, max_item_count=None):
        # type: (str, List, int) -> QueryIterable
        """Return all stored procedures matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryStoredProcedures(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_stored_procedure(self, id):
        # type: (str) -> Dict[str, Any]
        """
        Get the stored procedure identified by `id`.

        :param id: ID of the stored procedure to be retrieved.
        :returns: The stored procedure as a dict, if present in the container.

        """
        return self.client_connection.ReadStoredProcedure(
            sproc_link=self._get_resource_link(id, ScriptType.StoredProcedure)
        )

    def create_stored_procedure(self, body):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """ Create a stored procedure in the container.

        :param body: A dict-like object representing the sproc to create.
        :raises `HTTPFailure`:

        To replace an existing sproc, use the :func:`Container.scripts.replace_stored_procedure` method.

        """
        return self.client_connection.CreateStoredProcedure(
            collection_link=self.container_link,
            sproc=body
        )

    def replace_stored_procedure(self, id, body):
        # type: (str, Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified stored procedure if it exists in the container.

        :param id: Id of the sproc to be replaced.
        :param body: A dict-like object representing the sproc to replace.
        :raises `HTTPFailure`:

        """
        return self.client_connection.ReplaceStoredProcedure(
            sproc_link=self._get_resource_link(id, ScriptType.StoredProcedure),
            sproc=body
        )

    def delete_stored_procedure(self, id):
        # type: (str) -> None
        """ Delete the specified stored procedure from the container.

        :param id: Id of the stored procedure to delete from the container.
        :raises `HTTPFailure`: The sproc wasn't deleted successfully. If the sproc does not exist in the container, a `404` error is returned.

        """

        self.client_connection.DeleteStoredProcedure(
            sproc_link=self._get_resource_link(id, ScriptType.StoredProcedure)
        )

    def execute_stored_procedure(self, id, partition_key=None, enable_script_logging=None, params=None):
        # type: (str, str, list[Any]) -> Any
        """ execute the specified stored procedure.

        :param id: Id of the stored procedure to be executed.
        :param partition_key: Specifies the partition key to indicate which partition the sproc should execute on.

        :raises `HTTPFailure`

        """

        request_options = {}  # type: Dict[str, Any]
        if partition_key is not None:
            request_options["partitionKey"] = partition_key
        if enable_script_logging is not None:
            request_options["enableScriptLogging"] = enable_script_logging

        return self.client_connection.ExecuteStoredProcedure(
            sproc_link=self._get_resource_link(id, ScriptType.StoredProcedure),
            params=params,
            options=request_options
        )

    def list_triggers(self, max_item_count=None):
        # type: (int) -> QueryIterable
        """ List all triggers in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadTriggers(
            collection_link=self.container_link,
            options=request_options
        )

    def query_triggers(self, query, parameters=None, max_item_count=None):
        # type: (str, List, int) -> QueryIterable
        """Return all triggers matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryTriggers(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_trigger(self, id):
        # type: (str) -> Dict[str, Any]
        """
        Get the trigger identified by `id`.

        :param id: ID of the trigger to be retrieved.
        :returns: The trigger as a dict, if present in the container.

        """
        return self.client_connection.ReadTrigger(
            trigger_link=self._get_resource_link(id, ScriptType.Trigger)
        )

    def create_trigger(self, body):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """ Create a trigger in the container.

        :param body: A dict-like object representing the trigger to create.
        :raises `HTTPFailure`:

        To replace an existing trigger, use the :func:`Container.scripts.replace_trigger` method.

        """
        return self.client_connection.CreateTrigger(
            collection_link=self.container_link,
            trigger=body
        )

    def replace_trigger(self, id, body):
        # type: (str, Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified tigger if it exists in the container.
        :param id: Id of the trigger to be replaced.
        :param body: A dict-like object representing the trigger to replace.
        :raises `HTTPFailure`:

        """
        return self.client_connection.ReplaceTrigger(
            trigger_link=self._get_resource_link(id, ScriptType.Trigger),
            trigger=body
        )

    def delete_trigger(self, id):
        # type: (str) -> None
        """ Delete the specified trigger from the container.

        :param id: Id of the trigger to delete from the container.
        :raises `HTTPFailure`: The trigger wasn't deleted successfully. If the trigger does not exist in the container, a `404` error is returned.

        """

        self.client_connection.DeleteTrigger(
            trigger_link=self._get_resource_link(id, ScriptType.Trigger)
        )


    def list_user_defined_functions(self, max_item_count=None):
        # type: (int) -> QueryIterable
        """ List all user defined functions in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUserDefinedFunctions(
            collection_link=self.container_link,
            options=request_options
        )

    def query_user_defined_functions(self, query, parameters=None, max_item_count=None):
        # type: (str, List, int) -> QueryIterable
        """Return all user defined functions matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryUserDefinedFunctions(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_user_defined_function(self, id):
        # type: (str) -> Dict[str, Any]
        """
        Get the stored procedure identified by `id`.

        :param id: ID of the user defined function to be retrieved.
        :returns: The stored procedure as a dict, if present in the container.

        """
        return self.client_connection.ReadUserDefinedFunction(
            udf_link=self._get_resource_link(id, ScriptType.UserDefinedFunction)
        )

    def create_user_defined_function(self, body):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """ Create a user defined function in the container.

        :param body: A dict-like object representing the udf to create.
        :raises `HTTPFailure`:

        To replace an existing udf, use the :func:`Container.scripts.replace_user_defined_function` method.

        """
        return self.client_connection.CreateUserDefinedFunction(
            collection_link=self.container_link,
            udf=body
        )

    def replace_user_defined_function(self, id, body):
        # type: (str, Dict[str, Any]) -> Dict[str, Any]
        """ Replaces the specified user defined function if it exists in the container.

        :param id: Id of the udf to be replaced.
        :param body: A dict-like object representing the udf to replace.
        :raises `HTTPFailure`:

        """
        return self.client_connection.ReplaceUserDefinedFunction(
            udf_link=self._get_resource_link(id, ScriptType.UserDefinedFunction),
            udf=body
        )

    def delete_user_defined_function(self, id):
        # type: (str) -> None
        """ Delete the specified user defined function from the container.

        :param id: Id of the udf to delete from the container.
        :raises `HTTPFailure`: The udf wasn't deleted successfully. If the udf does not exist in the container, a `404` error is returned.

        """

        self.client_connection.DeleteUserDefinedFunction(
            udf_link=self._get_resource_link(id, ScriptType.UserDefinedFunction)
        )