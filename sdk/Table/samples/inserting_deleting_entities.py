class InsertDeleteEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

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

        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceExistsError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            entity = {"entity": None}
            inserted_entity = table_client.insert_entity(table_name=self.table_name, table_entity_properties=entity)
            print(inserted_entity)
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceExistsError:
            raise ResourceExistsError

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

        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            partition_key = 1
            row_key = 0
            deleted_entity = table_client.delete_entity(table_name=self.table_name, partition_key=partition_key,
                                                        row_key=row_key)
            print(deleted_entity)
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceNotFoundError:
            raise ResourceNotFoundError
