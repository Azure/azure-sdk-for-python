class InsertDeleteEntity(object):

    def insert_entity(self):
        """Insert entity in a table.

        :param

        table,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        response_preference=None,  # type: Optional[Union[str, "models.ResponseFormat"]]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any

        :return: dict mapping str to object, or the result of cls(response)
        :rtype: dict[str, object] or None
        :raises: ~azure.core.exceptions.HttpResponseError
        """


        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError
        from azure.storage.tables._generated.operations._service_operations import ResourceExistsError
        table_client = TableServiceClient(account_url=self.account_url,credential=self.credential)
        try:
            inserted_entity = table_client.insert_entity(table_name=self.table_name)
            print(inserted_entity)
        except HttpResponseError and ResourceExistsError:
            raise ResourceExistsError
            print(HttpResponseError.response)

    def delete_entity(self):
        """Deletes the specified entity in a table.

        :param

        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        if_match,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any

        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError
        from azure.storage.tables._generated.operations._service_operations import ResourceNotFoundError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.credential)
        try:
            deleted_entity = table_client.delete_entity(table_name=self.table_name)
            print(deleted_entity)
        except HttpResponseError and ResourceNotFoundError:
            raise ResourceNotFoundError
            print(HttpResponseError.response)