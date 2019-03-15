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

class Scripts:

    def __init__(self, client_connection, container, properties=None):
        # type: (CosmosClientConnection, Union[Container, str], str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.properties = properties
        self.collection_link = container.collection_link

    def list_stored_procedures(self, max_item_count=None):
        # type: (int) -> Dict[str, Any]
        """ List all stored procedures in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadStoredProcedures(
            collection_link=self.collection_link,
            options=request_options
        )

    def query_stored_procedures(self, query, parameters=None, max_item_count=None):
        pass

    def get_stored_procedure(self, id):
        pass

    def create_stored_procedure(self, body):
        pass

    def upsert_stored_procedure(self, body):
        pass

    def replace_stored_procedure(self, id, body):
        pass

    def delete_stored_procedure(self, id):
        pass

    def execute_stored_procedure(self, id, partition_key, options=None):
        pass



    def list_triggers(self, max_item_count=None):
        # type: (int) -> Dict[str, Any]
        """ List all triggers in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadTriggers(
            collection_link=self.collection_link,
            options=request_options
        )

    def query_triggers(self, query, parameters=None, max_item_count=None):
        pass

    def get_trigger(self, id):
        pass

    def create_trigger(self, body):
        pass

    def upsert_trigger(self, body):
        pass

    def replace_trigger(self, id, body):
        pass

    def delete_trigger(self, id):
        pass



    def list_user_defined_functions(self, max_item_count=None):
        # type: (int) -> Dict[str, Any]
        """ List all user defined functions in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUserDefinedFunctions(
            collection_link=self.collection_link,
            options=request_options
        )

    def query_user_defined_functions(self, query, parameters=None, max_item_count=None):
        pass

    def get_user_defined_function(self, id):
        pass

    def create_user_defined_function(self, body):
        pass

    def upsert_user_defined_function(self, body):
        pass

    def replace_user_defined_function(self, id, body):
        pass

    def delete_user_defined_function(self, id):
        pass
