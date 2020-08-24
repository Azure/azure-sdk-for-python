import os

class TableErrorHandling:
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    def create_table_if_exists(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        table_service_client.create_table(table_name=self.table_name)
        try:
            # try to create existing table, ResourceExistsError will be thrown
            table_service_client.create_table(table_name=self.table_name)
        except ResourceExistsError:
            print("Table already exists")


if __name__ == '__main__':
    sample = TableErrorHandling()
    sample.create_table_if_exists()