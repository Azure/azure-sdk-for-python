#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show managing rule entities under a ServiceBus Subscription, including
    - Create a rule
    - Create a rule with sql filter
    - Get rule properties.
    - Update a rule
    - Delete a rule
    - List rules under the given ServiceBus Namespace
"""

import os
import asyncio
import uuid
from azure.servicebus.management import SqlRuleFilter
from azure.servicebus.aio.management import ServiceBusAdministrationClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
TOPIC_NAME = os.environ['SERVICE_BUS_TOPIC_NAME']
SUBSCRIPTION_NAME = os.environ['SERVICE_BUS_SUBSCRIPTION_NAME']
RULE_NAME = "sb_mgmt_rule" + str(uuid.uuid4())
RULE_WITH_SQL_FILTER_NAME = "sb_sql_rule" + str(uuid.uuid4())


async def create_rule(servicebus_mgmt_client):
    print("-- Create Rule")
    await servicebus_mgmt_client.create_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_NAME)
    print("Rule {} is created.".format(RULE_NAME))
    print("")

    print("-- Create Rule with SQL Filter")
    sql_filter_parametrized = SqlRuleFilter(
        "property1 = @param1 AND property2 = @param2",
        parameters={
            "@param1": "value",
            "@param2" : 1
        }
    )
    await servicebus_mgmt_client.create_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_WITH_SQL_FILTER_NAME, filter=sql_filter_parametrized)
    print("Rule {} is created.".format(RULE_WITH_SQL_FILTER_NAME))
    print("")


async def delete_rule(servicebus_mgmt_client):
    print("-- Delete Rule")
    await servicebus_mgmt_client.delete_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_NAME)
    print("Rule {} is deleted.".format(RULE_NAME))
    await servicebus_mgmt_client.delete_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_WITH_SQL_FILTER_NAME)
    print("Rule {} is deleted.".format(RULE_WITH_SQL_FILTER_NAME))
    print("")


async def list_rules(servicebus_mgmt_client):
    print("-- List Rules")
    async for rule_properties in servicebus_mgmt_client.list_rules(TOPIC_NAME, SUBSCRIPTION_NAME):
        print("Rule Name:", rule_properties.name)
    print("")


async def get_and_update_rule(servicebus_mgmt_client):
    print("-- Get and Update Rule")
    rule_properties = await servicebus_mgmt_client.get_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_NAME)
    print("Rule Name:", rule_properties.name)
    print("Please refer to RuleProperties for complete available properties.")
    print("")

    # update by updating the properties in the model
    rule_properties.filter = SqlRuleFilter(
        "property1 = @param1 AND property2 = @param2",
        parameters={
            "@param1": "value2",
            "@param2": 2
        }
    )
    await servicebus_mgmt_client.update_rule(TOPIC_NAME, SUBSCRIPTION_NAME, rule_properties)

    # update by passing keyword arguments
    rule_properties = await servicebus_mgmt_client.get_rule(TOPIC_NAME, SUBSCRIPTION_NAME, RULE_NAME)
    await servicebus_mgmt_client.update_rule(
        TOPIC_NAME,
        SUBSCRIPTION_NAME,
        rule_properties,
        filter=SqlRuleFilter(
            "property1 = @param1 AND property2 = @param2",
            parameters={
                "@param1": "value3",
                "@param2": 3
            }
        )
    )


async def main():
    async with ServiceBusAdministrationClient.from_connection_string(CONNECTION_STR) as servicebus_mgmt_client:
        await create_rule(servicebus_mgmt_client)
        await list_rules(servicebus_mgmt_client)
        await get_and_update_rule(servicebus_mgmt_client)
        await delete_rule(servicebus_mgmt_client)

asyncio.run(main())
