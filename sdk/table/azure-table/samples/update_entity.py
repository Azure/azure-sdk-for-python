class UpdateEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    table_name = "OfficeSupplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # making keys not able to change - SEPARATE
    entity = {
        'PartitionKey': 'color',
        'RowKey': 'brand',
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def update_entity(self):
        from azure.table import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            # defaults to UpdateMode.merge
            table_client.update_entity(entity=self.entity)
        except HttpResponseError as e:
            print(e.response)

    def upsert_entity(self):
        from azure.table import TableClient
        from azure.core.exceptions import HttpResponseError
        from azure.table._models import UpdateMode

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_client.upsert_entity(entity=self.entity, mode=UpdateMode.replace)
        except HttpResponseError as e:
            print(e.response)
