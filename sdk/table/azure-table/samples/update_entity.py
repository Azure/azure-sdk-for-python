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
        from azure.core.exceptions import ResourceNotFoundError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)
        try:
            # defaults to UpdateMode.merge
            table_client.update_entity(entity=self.entity)
        except ResourceNotFoundError:
            print("Entity does not exist")

    def upsert_entity(self):
        from azure.table import TableClient
        from azure.table._models import UpdateMode

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)

        table_client.upsert_entity(entity=self.entity, mode=UpdateMode.replace)
        # no error will be thrown - it will insert
