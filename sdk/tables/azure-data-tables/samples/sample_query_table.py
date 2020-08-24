import os
import copy
import random

class SampleTablesQuery(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    entity_name = "marker"

    name_filter = "Name eq '{}'".format(entity_name)

    def _insert_random_entities(self):
        from azure.data.tables import TableClient
        brands = ["Crayola", "Sharpie", "Chameleon"]
        colors = ["red", "blue", "orange", "yellow"]
        names = ["marker", "pencil", "pen"]
        entity_template = {
            "PartitionKey": "pk",
            "RowKey": "row",
        }

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        table_client.create_table()

        for i in range(10):
            e = copy.deepcopy(entity_template)
            e["RowKey"] += str(i)
            e["Name"] = random.choice(names)
            e["Brand"] = random.choice(brands)
            e["Color"] = random.choice(colors)
            table_client.create_entity(entity=e)


    def sample_query_entities(self):
        self._insert_random_entities()
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

        try:
            queried_entities = table_client.query_entities(filter=self.name_filter, select=["Brand","Color"])

            for entity_chosen in queried_entities:
                print(entity_chosen)

        except HttpResponseError as e:
            print(e.message)

        finally:
            table_client.delete_table()

if __name__ == '__main__':
    stq = SampleTablesQuery()
    stq.sample_query_entities()