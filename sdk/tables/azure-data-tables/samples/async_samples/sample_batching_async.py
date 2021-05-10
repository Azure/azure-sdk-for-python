# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_batching.py

DESCRIPTION:
    These samples demonstrate how to use the batch transaction API to perform multiple
    operations within a single request

USAGE:
    python sample_batching.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""


from datetime import datetime, timedelta
import os
from time import sleep
import asyncio
from dotenv import find_dotenv, load_dotenv


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name = "sampleTransactionAsync"

    async def _create_entities(self):
        from azure.core.exceptions import ResourceExistsError

        self.entity1 = {"PartitionKey": "pk001", "RowKey": "rk001", "Value": 4, "day": "Monday", "float": 4.003}
        self.entity2 = {"PartitionKey": "pk001", "RowKey": "rk002", "Value": 4, "day": "Tuesday", "float": 4.003}
        self.entity3 = {"PartitionKey": "pk001", "RowKey": "rk003", "Value": 4, "day": "Wednesday", "float": 4.003}
        self.entity4 = {"PartitionKey": "pk001", "RowKey": "rk004", "Value": 4, "day": "Thursday", "float": 4.003}

        entities = [self.entity2, self.entity3, self.entity4]

        for entity in entities:
            try:
                await self.table_client.create_entity(entity)
            except ResourceExistsError:
                print("entity already exists")
                pass

    async def sample_transaction(self):
        # Instantiate a TableServiceClient using a connection string

        # [START batching]
        from azure.data.tables.aio import TableClient
        from azure.data.tables import TableTransactionError
        from azure.core.exceptions import ResourceExistsError

        self.table_client = TableClient.from_connection_string(
            conn_str=self.connection_string, table_name=self.table_name
        )

        try:
            await self.table_client.create_table()
            print("Created table")
        except ResourceExistsError:
            print("Table already exists")

        await self._create_entities()

        operations = [
            ("create", self.entity1),
            ("delete", self.entity2),
            ("upsert", self.entity3),
            ("update", self.entity4, {"mode": "replace"}),
        ]
        try:
            await self.table_client.submit_transaction(operations)
        except TableTransactionError as e:
            print("There was an error with the transaction operation")
            print("Error: {}".format(e))
        # [END batching]

    async def clean_up(self):
        await self.table_client.delete_table()
        await self.table_client.__aexit__()


async def main():
    sample = CreateClients()
    await sample.sample_transaction()
    await sample.clean_up()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
