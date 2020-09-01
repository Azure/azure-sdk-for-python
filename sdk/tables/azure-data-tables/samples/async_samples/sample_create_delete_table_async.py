import os
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class CreateDeleteTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"


    async def create_table(self):
        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_item = await table_service_client.create_table(table_name=self.table_name)
            print("Created table {}!".format(table_item.table_name))
        except ResourceExistsError:
            print("Table already exists")

    async def create_if_not_exists(self):
        from azure.data.tables.aio import TableServiceClient

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        table_item = TableServiceClient.create_table_if_not_exists(table_name=self.table_name)
        print("Table name: {}".format(table_item.table_name))


    async def delete_table(self):
        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            await table_service_client.delete_table(table_name=self.table_name)
            print("Deleted table {}!".format(self.table_name))
        except ResourceNotFoundError:
            print("Table could not be found")


    async def create_from_table_client(self):
        from azure.data.table import TableClient

        table_client = TableClient.from_connection_string(
            conn_str=self.connection_string,
            table_name=self.table_name
        )
        try:
            table_item = await table_client.create_table()
            print("Created table {}!".format(table_item.table_name))
        except ResourceExistsError:
            print("Table already exists")


    async def delete_from_table_client(self):
        from azure.data.table import TableClient

        table_client = TableClient.from_connection_string(
            conn_str=self.connection_string,
            table_name=self.table_name
        )
        try:
            await table_client.delete_table()
            print("Deleted table {}!".format(self.table_name))
        except ResourceExistsError:
            print("Table already exists")


async def main():
    sample = CreateDeleteTable()
    await sample.create_table()
    await sample.delete_table()


if __name__ == '__main__':
    asyncio.run(main())
