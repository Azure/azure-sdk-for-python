#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show selecting a message into Subscriptions on a Topic using various Filters asynchronously.
"""

import os
import time
import asyncio
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.servicebus.aio.management import ServiceBusAdministrationClient
from azure.servicebus.management import (
    TrueRuleFilter,
    SqlRuleFilter,
    SqlRuleAction,
    CorrelationRuleFilter
)
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
TOPIC_NAME = os.environ['SERVICE_BUS_TOPIC_NAME']
ALL_MSGS_SUBSCRIPTION_NAME = 'sb-allmsgs-sub'
SQL_FILTER_ONLY_SUBSCRIPTION_NAME = 'sb-sqlfilteronly-sub'
SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME = 'sb-sqlfilteraction-sub'
CORRELATION_FILTER_SUBSCRIPTION_NAME = 'sb-corrfiltersub'

async def create_rules_with_filter(servicebus_mgmt_client):
    # First subscription is already created with default rule. Leave as is.
    print("SubscriptionName: {}, Removing and re-adding Default Rule".format(ALL_MSGS_SUBSCRIPTION_NAME))
    await create_rule_with_filter(
        servicebus_mgmt_client,
        ALL_MSGS_SUBSCRIPTION_NAME,
        "$Default",
        filter=TrueRuleFilter()
    )

    # Second subscription: Add required SqlRuleFilter Rule.
    print("SubscriptionName: {}, Removing Default Rule and Adding SqlRuleFilter.".format(SQL_FILTER_ONLY_SUBSCRIPTION_NAME))
    await create_rule_with_filter(
        servicebus_mgmt_client,
        SQL_FILTER_ONLY_SUBSCRIPTION_NAME,
        "RedSqlRule",
        filter=SqlRuleFilter("Color = 'Red'")
    )

    # Third subscription: Add SqlRuleFilter and SqlRuleAction.
    print("SubscriptionName: {}, Removing Default Rule and Adding SqlRuleFilter and SqlRuleAction".format(SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME))
    await create_rule_with_filter(
        servicebus_mgmt_client,
        SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME,
        "BlueSqlRule",
        filter=SqlRuleFilter("Color = 'Blue'"),
        action=SqlRuleAction("SET Color = 'BlueProcessed'")
    )

    # Fourth subscription: Add CorrelationRuleFilter.
    print("SubscriptionName: {}, Removing Default Rule and Adding CorrelationRuleFilter".format(CORRELATION_FILTER_SUBSCRIPTION_NAME))
    await create_rule_with_filter(
        servicebus_mgmt_client,
        CORRELATION_FILTER_SUBSCRIPTION_NAME,
        "ImportantCorrelationRule",
        filter=CorrelationRuleFilter(correlation_id='important', label="Red")
    )

    # Get rules on subscription, called here only for one subscription as an example.
    print("SubscriptionName: {}".format(CORRELATION_FILTER_SUBSCRIPTION_NAME))
    async for rule in servicebus_mgmt_client.list_rules(TOPIC_NAME, CORRELATION_FILTER_SUBSCRIPTION_NAME):
        print("Rule {}; Filter: {}".format(rule.name, type(rule.filter).__name__))

async def create_rule_with_filter(servicebus_mgmt_client, subscription_name, filter_name, filter, action=None):
    try:
        await servicebus_mgmt_client.delete_rule(TOPIC_NAME, subscription_name, "$Default")
    except ResourceNotFoundError:
        pass
    try:
        await servicebus_mgmt_client.create_rule(
            TOPIC_NAME,
            subscription_name,
            filter_name,
            filter=filter,
            action=action
        )
    except ResourceExistsError:
        pass

async def send_messages():
    servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STR)
    print("====================== Sending messages to topic ======================")
    msgs_to_send = []
    async with servicebus_client.get_topic_sender(topic_name=TOPIC_NAME) as sender:
        msgs_to_send.append(create_message(label="Red"))
        msgs_to_send.append(create_message(label="Blue"))
        msgs_to_send.append(create_message(label="Red", correlation_id="important"))
        msgs_to_send.append(create_message(label="Blue", correlation_id="important"))
        msgs_to_send.append(create_message(label="Red", correlation_id="notimportant"))
        msgs_to_send.append(create_message(label="Blue", correlation_id="notimportant"))
        msgs_to_send.append(create_message(label="Green"))
        msgs_to_send.append(create_message(label="Green", correlation_id="important"))
        msgs_to_send.append(create_message(label="Green", correlation_id="notimportant"))
        await sender.send_messages(msgs_to_send)

def create_message(label, correlation_id=None):
    return ServiceBusMessage("Rule with filter sample", application_properties={"Color": label}, subject=label, correlation_id=correlation_id)

async def receive_messages(servicebus_client, subscription_name):
    async with servicebus_client:
        receiver = servicebus_client.get_subscription_receiver(
            topic_name=TOPIC_NAME,
            subscription_name=subscription_name
        )
        async with receiver:
            print("==========================================================================")
            print("Receiving Messages From Subscription: {}".format(subscription_name))
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            for msg in received_msgs:
                color = msg.application_properties.get(b'Color').decode()
                correlation_id = msg.correlation_id
                print("Color Property = {}, Correlation ID = {}".format(color, correlation_id))
                await receiver.complete_message(msg)
            print("'{}' Messages From Subscription: {}".format(len(received_msgs), subscription_name))
            print("==========================================================================")

async def create_subscription(servicebus_mgmt_client, subscription_name):
    try:
        await servicebus_mgmt_client.create_subscription(TOPIC_NAME, subscription_name)
    except ResourceExistsError:
        pass
    print("Subscription {} is created.".format(subscription_name))

async def delete_subscription(servicebus_mgmt_client, subscription_name):
    try:
        await servicebus_mgmt_client.delete_subscription(TOPIC_NAME, subscription_name)
    except ResourceNotFoundError:
        pass
    print("Subscription {} is deleted.".format(subscription_name))

async def main():
    servicebus_mgmt_client = ServiceBusAdministrationClient.from_connection_string(CONNECTION_STR)
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    # Create subscriptions.
    await create_subscription(servicebus_mgmt_client, ALL_MSGS_SUBSCRIPTION_NAME)
    await create_subscription(servicebus_mgmt_client, SQL_FILTER_ONLY_SUBSCRIPTION_NAME)
    await create_subscription(servicebus_mgmt_client, SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME)
    await create_subscription(servicebus_mgmt_client, CORRELATION_FILTER_SUBSCRIPTION_NAME)

    # Create rules
    await create_rules_with_filter(servicebus_mgmt_client)
        
    # Send messages to topic
    await send_messages()

    # Receive messages from 'ALL_MSGS_SUBSCRIPTION_NAME'. Should receive all 9 messages.
    await receive_messages(servicebus_client, ALL_MSGS_SUBSCRIPTION_NAME)

    # Receive messages from 'SQL_FILTER_ONLY_SUBSCRIPTION_NAME'. Should receive all messages with Color = 'Red' i.e 3 messages
    await receive_messages(servicebus_client, SQL_FILTER_ONLY_SUBSCRIPTION_NAME)

    # Receive messages from 'SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME'. Should receive all messages with Color = 'Blue'
    # i.e 3 messages AND all messages should have color set to 'BlueProcessed'
    await receive_messages(servicebus_client, SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME)

    # Receive messages from 'CORRELATION_FILTER_SUBSCRIPTION_NAME'. Should receive all messages  with Color = 'Red' and CorrelationId = "important"
    # i.e 1 message
    await receive_messages(servicebus_client, CORRELATION_FILTER_SUBSCRIPTION_NAME)

    # Delete subscriptions.
    await delete_subscription(servicebus_mgmt_client, ALL_MSGS_SUBSCRIPTION_NAME)
    await delete_subscription(servicebus_mgmt_client, SQL_FILTER_ONLY_SUBSCRIPTION_NAME)
    await delete_subscription(servicebus_mgmt_client, SQL_FILTER_WITH_ACTION_SUBSCRIPTION_NAME)
    await delete_subscription(servicebus_mgmt_client, CORRELATION_FILTER_SUBSCRIPTION_NAME)

    await servicebus_mgmt_client.close()
    await servicebus_client.close()


asyncio.run(main())
