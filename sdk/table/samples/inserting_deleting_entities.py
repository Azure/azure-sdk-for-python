class InsertDeleteEntity(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # Assuming there is a created table
    partition_key = "Crayola Marker"
    row_key = "Marker"
    entity = {
        'product': 'Marker', 'color': 'Purple', 'price': '$5'}

    def insert_entity(self):

        from azure.azure_table import TableClient
        from azure.core.exceptions import HttpResponseError, ResourceExistsError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            inserted_entity = table_client.insert_entity(partition_key=self.partition_key,
                                                         row_key=self.row_key,
                                                         table_entity_properties=self.entity)
            # inserted_entity type is dict[str,object]
            print(inserted_entity.items())  # print out key-value pair of entity
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceExistsError:
            raise ResourceExistsError

    def delete_entity(self):

        from azure.azure_table import TableClient
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_client.delete_entity(partition_key=self.partition_key,
                                       row_key=self.row_key)
            # deleted_entity type is None
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceNotFoundError:
            raise ResourceNotFoundError
