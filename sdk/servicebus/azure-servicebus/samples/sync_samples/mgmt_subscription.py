#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show managing subscription entities under a ServiceBus Namespace, including
    - Create a subscription
    - Get subscription properties and runtime information
    - Update a subscription
    - Delete a subscription
    - List subscriptions under the given ServiceBus Namespace
"""

# pylint: disable=C0111

import os
import uuid
from azure.servicebus.management import ServiceBusAdministrationClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
TOPIC_NAME = os.environ['SERVICE_BUS_TOPIC_NAME']
SUBSCRIPTION_NAME = "sb_mgmt_sub" + str(uuid.uuid4())



def create_subscription(servicebus_mgmt_client):
    print("-- Create Subscription")
    servicebus_mgmt_client.create_subscription(TOPIC_NAME, SUBSCRIPTION_NAME)
    print("Subscription {} is created.".format(SUBSCRIPTION_NAME))
    print("")


def delete_subscription(servicebus_mgmt_client):
    print("-- Delete Subscription")
    servicebus_mgmt_client.delete_subscription(TOPIC_NAME, SUBSCRIPTION_NAME)
    print("Subscription {} is deleted.".format(SUBSCRIPTION_NAME))
    print("")


def list_subscriptions(servicebus_mgmt_client):
    print("-- List Subscriptions")
    for subscription_properties in servicebus_mgmt_client.list_subscriptions(TOPIC_NAME):
        print("Subscription Name:", subscription_properties.name)
    print("")


def get_and_update_subscription(servicebus_mgmt_client):
    print("-- Get and Update Subscription")
    subscription_properties = servicebus_mgmt_client.get_subscription(TOPIC_NAME, SUBSCRIPTION_NAME)
    print("Subscription Name:", subscription_properties.name)
    print("Please refer to SubscriptionDescription for complete available settings.")
    print("")
    subscription_properties.max_delivery_count = 5
    servicebus_mgmt_client.update_subscription(TOPIC_NAME, subscription_properties)


def get_subscription_runtime_properties(servicebus_mgmt_client):
    print("-- Get Subscription Runtime Properties")
    get_subscription_runtime_properties = servicebus_mgmt_client.get_subscription_runtime_properties(TOPIC_NAME, SUBSCRIPTION_NAME)
    print("Subscription Name:", get_subscription_runtime_properties.name)
    print("Please refer to SubscriptionRuntimeProperties from complete available runtime properties.")
    print("")


with ServiceBusAdministrationClient.from_connection_string(CONNECTION_STR) as servicebus_mgmt_client:
    create_subscription(servicebus_mgmt_client)
    list_subscriptions(servicebus_mgmt_client)
    get_and_update_subscription(servicebus_mgmt_client)
    get_subscription_runtime_properties(servicebus_mgmt_client)
    delete_subscription(servicebus_mgmt_client)
