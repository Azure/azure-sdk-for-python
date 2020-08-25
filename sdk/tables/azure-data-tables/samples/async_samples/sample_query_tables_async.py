import os
import asyncio

class QueryTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"

    # Creating query filter for that table
    name_filter = "TableName eq '{}'".format(table_name)

    @classmethod
    async def query_tables(self):
        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)

        # Create Tables to query
        try:
            my_table = await table_service_client.create_table(table_name=self.table_name)
        except ResourceExistsError:
            pass

        # Query tables
        queried_tables = await table_service_client.query_tables(filter=self.name_filter, results_per_page=10)

        for table in queried_tables:
            print(table.table_name)


async def main():
    await QueryTable.query_tables()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())