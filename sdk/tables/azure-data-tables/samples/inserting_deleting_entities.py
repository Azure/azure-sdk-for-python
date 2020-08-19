import os

class InsertDeleteEntity(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    # Assuming there is a created table
    entity = {
        'PartitionKey': 'color',
        'RowKey': 'brand',
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def create_entity(self):

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError

        # table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

        try:
            inserted_entity = table_client.create_entity(entity=self.entity)

            print(inserted_entity.items())  # print out key-value pair of entity
        except ResourceExistsError:
            print("Entity already exists")

    def delete_entity(self):

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
        from azure.core import MatchConditions

        # table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

        # Create entity to delete (to showcase etag)
        try:
            entity_created = table_client.create_entity(entity=self.entity)
        except ResourceExistsError as e:
            print("Entity already exists!")

        try:
            # will delete if match_condition and etag are satisfied
            table_client.delete_entity(row_key=self.entity["RowKey"], partition_key=self.entity["PartitionKey"])
            print("Successfully deleted!")

        except ResourceNotFoundError:
            print("Entity does not exists")


if __name__ == '__main__':
    ide = InsertDeleteEntity()
    ide.create_entity()
    ide.delete_entity()