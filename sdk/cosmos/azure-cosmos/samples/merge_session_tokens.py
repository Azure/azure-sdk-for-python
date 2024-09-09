# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
import datetime

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to merge session tokens using different strategies for storing the session token
# ----------------------------------------------------------------------------------------------------------



# url = os.environ["ACCOUNT_URI"]
# key = os.environ["ACCOUNT_KEY"]
# client = CosmosClient(url, key)
# # Create a database in the account using the CosmosClient,
# # specifying that the operation shouldn't throw an exception
# # if a database with the given ID already exists.
# # [START create_database]
# database_name = "testDatabase"
# try:
#     database = client.create_database(id=database_name)
# except exceptions.CosmosResourceExistsError:
#     database = client.get_database_client(database=database_name)
# # [END create_database]
#
# # Create a container, handling the exception if a container with the
# # same ID (name) already exists in the database.
# # [START create_container]
# container_name = "products"
# try:
#     container = database.create_container(
#         id=container_name, partition_key=PartitionKey(path="/productName")
#     )
# except exceptions.CosmosResourceExistsError:
#     container = database.get_container_client(container_name)
# # [END create_container]
#
# # This would be happening through different clients
# # Using physical partition model for read operations
# cache = {}
# session_token = ""
# feed_range = container.feed_range_for_logical_partition(logical_pk)
# for stored_feed_range, stored_session_token in cache:
#     if is_feed_range_subset(stored_feed_range, feed_range):
#         session_token = stored_session_token
# read_item = container.read_item(doc_to_read, logical_pk, session_token)
#
# # the feed range returned in the request context will correspond to the logical partition key
# logical_pk_feed_range = container.client_connection.last_response_headers["request-context"]["feed-range"]
# session_token = container.client_connection.last_response_headers["request-context"]["session-token"]
# feed_ranges_and_session_tokens = []
#
# # Get feed ranges for physical partitions
# container_feed_ranges = container.read_feed_ranges()
# target_feed_range = ""
#
# # which feed range maps to the logical pk from the operation
# for feed_range in container_feed_ranges:
#     if is_feed_range_subset(feed_range, logical_pk_feed_range):
#         target_feed_range = feed_range
#         break
# for cached_feed_range, cached_session_token in cache:
#     feed_ranges_and_session_tokens.append((cached_feed_range, cached_session_token))
# # Add the target feed range and session token from the operation
# feed_ranges_and_session_tokens.append((target_feed_range, session_token))
# cache[feed_range] = container.get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
#
#
#
# # Different ways of storing the session token and how to get most updated session token
#
# # ---------------------1. using logical partition key ---------------------------------------------------
# # could also use the one stored from the responses headers
# target_feed_range = container.feed_range_for_logical_partition(logical_pk)
# updated_session_token = container.get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
# # ---------------------2. using artificial feed range ----------------------------------------------------
# # Get four artificial feed ranges
# container_feed_ranges = container.read_feed_ranges(4)
#
# pk_feed_range = container.feed_range_for_logical_partition(logical_pk)
# target_feed_range = ""
# # which feed range maps to the logical pk from the operation
# for feed_range in container_feed_ranges:
#     if is_feed_range_subset(feed_range, pk_feed_range):
#         target_feed_range = feed_range
#         break
#
# updated_session_token = container.get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
# # ---------------------3. using physical partitions -----------------------------------------------------
# # Get feed ranges for physical partitions
# container_feed_ranges = container.read_feed_ranges()
#
# pk_feed_range = container.feed_range_for_logical_partition(logical_pk)
# target_feed_range = ""
# # which feed range maps to the logical pk from the operation
# for feed_range in container_feed_ranges:
#     if is_feed_range_subset(feed_range, pk_feed_range):
#         target_feed_range = feed_range
#         break
#
# updated_session_token = container.get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
# # ------------------------------------------------------------------------------------------------------