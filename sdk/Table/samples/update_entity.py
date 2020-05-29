class UpdateEntity(object):
    def update_entity(self):
        """Update entity in a table.

            :param

        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        if_match=None,  # type: Optional[str]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any

                :return: None, or the result of cls(response)
                :rtype: None
                :raises: ~azure.core.exceptions.HttpResponseError
                """
        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.credential)
        try:
            updated_entity = table_client.update_entity(table_name=self.table_name, partition_key=self.partition_key
                                                        , row_key=self.row_key)
        except HttpResponseError as e:
            print(e.response)
        return updated_entity
