class UpdateEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    table_name = "OfficeSupplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    partition_key = "1"
    row_key = "1"
    # making keys not able to change - SEPARATE
    entity = {
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def update_entity(self):
        from azure.table import TableClient
        from azure.core.exceptions import HttpResponseError
        from azure.table._models import UpdateMode

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_client.update_entity(mode=UpdateMode.merge, partition_key=self.partition_key, row_key=self.row_key,
                                       table_entity_properties=self.entity)
        except HttpResponseError as e:
            print(e.response)

    def upsert_entity(self):
        from azure.table import TableClient
        from azure.core.exceptions import HttpResponseError
        from azure.table._models import UpdateMode

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_client.upsert_entity(mode=UpdateMode.replace, partition_key=self.partition_key, row_key=self.row_key,
                                       table_entity_properties=self.entity)
        except HttpResponseError as e:
            print(e.response)
