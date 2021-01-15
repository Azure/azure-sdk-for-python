class CreateODataQuery(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey" \
                        "=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net "
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    partition_key = "color"
    row_key = "brand"
    # Creating query filter for that table
    table_name = "Office Supplies"
    entity_name = "marker"
    name_filter = "EntityName eq '{}'".format(entity_name)

    def sample_query_entities(self):

        from azure.table import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)
        try:
            queried_entities = table_client.query_entities(filter=self.name_filter, select="brand,color")

            # queried_entities type is ItemPaged
            for entity_chosen in queried_entities:
                # create a list of the entities and iterate through them to print each one out
                # calls to the service to get more entities are made without user knowledge
                print(entity_chosen)
        except HttpResponseError as e:
            print(e.message)
