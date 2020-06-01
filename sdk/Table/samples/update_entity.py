class UpdateEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="
    partition_key = "1"
    row_key = "1"

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
        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            updated_entity = table_client.update_entity(table_name=self.table_name, partition_key=self.partition_key
                                                        , row_key=self.row_key)
            return updated_entity
        except HttpResponseError as e:
            print(e.response)
