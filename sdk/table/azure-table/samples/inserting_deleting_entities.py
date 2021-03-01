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

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)
        try:
            inserted_entity = table_client.create_entity(entity=self.entity)
            # inserted_entity type is dict[str,object]
            print(inserted_entity.items())  # print out key-value pair of entity
        except ResourceExistsError:
            print("EntityExists")

    def delete_entity(self):

        from azure.table import TableClient
        from azure.core.exceptions import ResourceNotFoundError
        from azure.core import MatchConditions

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)

        # Create entity to delete (to showcase etag)
        entity_created = table_client.create_entity(entity=self.entity)

        # show without calling metadata, cannot access etag
        try:
            entity_created.etag
        except AttributeError:
            print("Need to get metadata of entity")

        # In order to access etag as a part of the entity, need to call metadata on the entity
        metadata = entity_created.metadata()

        # Can now get etag
        etag = metadata['etag']

        try:
            # will delete if match_condition and etag are satisfied
            table_client.delete_entity(entity=self.entity, etag=etag, match_condition=MatchConditions.IfNotModified)

        except ResourceNotFoundError:
            print("EntityDoesNotExists")
