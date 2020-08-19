import os

class CreateODataQuery(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    entity_name = "marker"

    name_filter = "EntityName eq '{}'".format(entity_name)

    @classmethod
    def sample_query_entities(self):

        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

        try:
            queried_entities = table_client.query_entities(filter=self.name_filter, select="brand,color")

            for entity_chosen in queried_entities:
                print(entity_chosen)

        except HttpResponseError as e:
            print(e.message)

if __name__ == '__main__':
    CreateODataQuery.sample_query_entities()