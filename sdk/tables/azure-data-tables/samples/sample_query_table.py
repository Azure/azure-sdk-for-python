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

from dotenv import find_dotenv, load_dotenv


class SampleTablesQuery(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

    def insert_random_entities(self):
        import copy
        import os
        import random

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

        brands = [u"Crayola", u"Sharpie", u"Chameleon"]
        colors = [u"red", u"blue", u"orange", u"yellow"]
        names = [u"marker", u"pencil", u"pen"]
        entity_template = {
            u"PartitionKey": u"pk",
            u"RowKey": u"row",
        }

        with TableClient.from_connection_string(connection_string, table_name) as table_client:
            try:
                table_client.create_table()
            except ResourceExistsError:
                print(u"Table already exists")

            for i in range(25):
                e = copy.deepcopy(entity_template)
                try:
                    e[u"RowKey"] += unicode(i)
                except NameError:
                    e[u"RowKey"] += str(i)
                e[u"Name"] = random.choice(names)
                e[u"Brand"] = random.choice(brands)
                e[u"Color"] = random.choice(colors)
                e[u"Value"] = random.randint(0, 100)
                table_client.create_entity(entity=e)

    def sample_query_entities(self):
        # [START query_entities]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        print("Entities with name: marker")
        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

        with TableClient.from_connection_string(connection_string, table_name) as table_client:
            try:
                parameters = {u"name": u"marker"}
                name_filter = u"Name eq @name"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=[u"Brand", u"Color"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def sample_query_entities_multiple_params(self):
        # [START query_entities]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

        print("Entities with name: marker and brand: Crayola")
        with TableClient.from_connection_string(connection_string, table_name) as table_client:
            try:
                parameters = {u"name": u"marker", u"brand": u"Crayola"}
                name_filter = u"Name eq @name and Brand eq @brand"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=[u"Brand", u"Color"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def sample_query_entities_values(self):
        # [START query_entities]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

        print("Entities with 25 < Value < 50")
        with TableClient.from_connection_string(connection_string, table_name) as table_client:
            try:
                parameters = {u"lower": 25, u"upper": 50}
                name_filter = u"Value gt @lower and Value lt @upper"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=[u"Value"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def clean_up(self):
        import os

        from azure.data.tables import TableClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTable"

        with TableClient.from_connection_string(connection_string, table_name) as table_client:
            table_client.delete_table()


if __name__ == "__main__":
    stq = SampleTablesQuery()
    stq.insert_random_entities()
    stq.sample_query_entities()
    stq.sample_query_entities_multiple_params()
    stq.sample_query_entities_values()
    stq.clean_up()
