# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_query_table.py

DESCRIPTION:
    These samples demonstrate the following: querying a table for entities.

USAGE:
    python sample_query_table.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import copy
import random
from dotenv import find_dotenv, load_dotenv


class SampleTablesQuery(object):

    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.account_url = "{}.table.{}".format(self.account_name, self.endpoint)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name,
            self.access_key,
            self.endpoint
        )
        self.table_name = "SampleQueryTable"


    def _insert_random_entities(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError
        brands = [u"Crayola", u"Sharpie", u"Chameleon"]
        colors = [u"red", u"blue", u"orange", u"yellow"]
        names = [u"marker", u"pencil", u"pen"]
        entity_template = {
            u"PartitionKey": u"pk",
            u"RowKey": u"row",
        }

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        try:
            table_client.create_table()
        except ResourceExistsError:
            print(u"Table already exists")

        for i in range(10):
            e = copy.deepcopy(entity_template)
            try:
                e[u"RowKey"] += unicode(i)
            except NameError:
                e[u"RowKey"] += str(i)
            e[u"Name"] = random.choice(names)
            e[u"Brand"] = random.choice(brands)
            e[u"Color"] = random.choice(colors)
            table_client.create_entity(entity=e)


    def sample_query_entities(self):
        self._insert_random_entities()
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        # [START query_entities]
        try:
            entity_name = u"marker"
            name_filter = u"Name eq '{}'".format(entity_name)
            queried_entities = table_client.query_entities(filter=name_filter, select=[u"Brand",u"Color"])

            for entity_chosen in queried_entities:
                print(entity_chosen)

        except HttpResponseError as e:
            print(e.message)
        # [END query_entities]

        finally:
            table_client.delete_table()

if __name__ == '__main__':
    stq = SampleTablesQuery()
    stq.sample_query_entities()