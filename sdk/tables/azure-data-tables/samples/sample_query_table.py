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
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""

import os
import copy
import random
from dotenv import find_dotenv, load_dotenv


class SampleTablesQuery(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name = "SampleQueryTable"

    def insert_random_entities(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError

        brands = ["Crayola", "Sharpie", "Chameleon"]
        colors = ["red", "blue", "orange", "yellow"]
        names = ["marker", "pencil", "pen"]
        entity_template = {
            "PartitionKey": "pk",
            "RowKey": "row",
        }

        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                table_client.create_table()
            except ResourceExistsError:
                print(u"Table already exists")

            for i in range(25):
                e = copy.deepcopy(entity_template)
                e["RowKey"] += str(i)
                e["Name"] = random.choice(names)
                e["Brand"] = random.choice(brands)
                e["Color"] = random.choice(colors)
                e["Value"] = random.randint(0, 100)
                table_client.create_entity(entity=e)

    def sample_query_entities(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        print("Entities with name: marker")
        # [START query_entities]
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                parameters = {"name": "marker"}
                name_filter = "Name eq @name"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=["Brand", "Color"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def sample_query_entities_without_metadata(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        print("Entities with name: marker")
        # [START query_entities]
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                parameters = {"name": "marker"}
                name_filter = "Name eq @name"
                headers = {"Accept" : "application/json;odata=nometadata"}
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=["Brand", "Color"], parameters=parameters, headers=headers
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def sample_query_entities_multiple_params(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        print("Entities with name: marker and brand: Crayola")
        # [START query_entities]
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                parameters = {"name": "marker", "brand": "Crayola"}
                name_filter = "Name eq @name and Brand eq @brand"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=["Brand", "Color"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def sample_query_entities_values(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import HttpResponseError

        print("Entities with 25 < Value < 50")
        # [START query_entities]
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                parameters = {"lower": 25, "upper": 50}
                name_filter = "Value gt @lower and Value lt @upper"
                queried_entities = table_client.query_entities(
                    query_filter=name_filter, select=["Value"], parameters=parameters
                )

                for entity_chosen in queried_entities:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    def clean_up(self):
        from azure.data.tables import TableClient

        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            table_client.delete_table()


if __name__ == "__main__":
    stq = SampleTablesQuery()
    try:
        stq.insert_random_entities()
        stq.sample_query_entities()
        stq.sample_query_entities_without_metadata()
        stq.sample_query_entities_multiple_params()
        stq.sample_query_entities_values()
    except:
        stq.clean_up()
