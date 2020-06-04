from azure.azure_table._generated.models import QueryOptions


class CreateODataQuery(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    table_name = "NAME"
    entity_name = "name"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # Assuming there is a created table
    partition_key = "1"
    row_key = "1"
    # Creating query filter for that table
    # query_options = QueryOptions(select='name')
    name_filter = "EntityName eq '{}'".format(entity_name)

    def create_query_entities(self):

        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            queried_entities = table_client.query_table_entities(table_name=self.table_name,
                                                                 query_options=self.name_filter)

            # queried_entities type is ItemPaged
            for entity_chosen in list(queried_entities):
                # create a list of the entities and iterate through them to print each one out
                # calls to the service to get more entities are made without user knowledge
                print(entity_chosen)
        except HttpResponseError as e:
            print(e.message)
