import os
import logging

_LOGGER = logging.getLogger(__name__)

class CreateDeleteTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"


    def create_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_created = table_service_client.create_table(table_name=self.table_name)
            print("Created table {}!".format(table_created.table_name))
        except ResourceExistsError:
            print("Table already exists")


    def delete_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_service_client.delete_table(table_name=self.table_name)
            print("Deleted table {}!".format(self.table_name))
        except ResourceNotFoundError:
            print("Table could not be found")


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    sample.delete_table()
