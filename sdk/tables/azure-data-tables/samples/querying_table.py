import os

class QueryTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    # Creating query filter for that table
    name_filter = "TableName eq '{}'".format(table_name)

    @classmethod
    def query_tables(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)

        # Create Tables to query
        try:
            my_table = table_service_client.create_table(table_name=self.table_name)
            print(my_table.table_name)
        except ResourceExistsError:
            print("Table already exists!")

        # Query tables
        queried_tables = table_service_client.query_tables(filter=self.name_filter, results_per_page=10)

        for table in queried_tables:
            print(table.table_name)

if __name__ == "__main__":
    QueryTable.query_tables()