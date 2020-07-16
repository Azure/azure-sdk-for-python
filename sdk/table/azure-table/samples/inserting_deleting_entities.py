class InsertDeleteEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # Assuming there is a created table
    entity = {
        'PartitionKey': 'color',
        'RowKey': 'brand',
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def create_entity(self):

        from azure.table import TableClient
        from azure.core.exceptions import ResourceExistsError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            inserted_entity = table_client.create_entity(table_entity_properties=self.entity)
            # inserted_entity type is dict[str,object]
            print(inserted_entity.items())  # print out key-value pair of entity
        except ResourceExistsError:
            print("EntityExists")

    def delete_entity(self):

        from azure.table import TableClient
        from azure.core.exceptions import ResourceNotFoundError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_client.delete_entity(table_entity_properties=self.entity)

        except ResourceNotFoundError:
            print("EntityDoesNotExists")
