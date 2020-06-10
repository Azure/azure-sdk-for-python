class UpdateEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    table_name = "Office Supplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    partition_key = "1"
    row_key = "1"

    entity = {
        'PartitionKey': 'test',
        'RowKey': 'test1',
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def update_entity(self):

        from azure.azure_table import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            updated_entity = table_client.update_entity(table_name=self.table_name, partition_key=self.partition_key
                                                        , row_key=self.row_key, table_entity_properties=self.entity)
            # updated_entity type is None
        except HttpResponseError as e:
            print(e.response)
