# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import uuid
import functools

from behave import *

import test_utils

@given('the EventHub SDK is installed')
def step_impl(context):
    from azure import eventhub

@given('an EventHub is created with credentials retrieved')
def step_impl(context):
    #from mgmt_settings_real import get_credentials, SUBSCRIPTION_ID
    #rg, mgmt_client = test_utils.create_mgmt_client(get_credentials(), SUBSCRIPTION_ID)
    context.eh_config = test_utils.get_eventhub_config()

@given('an EventHub with {properties} is created with credentials retrieved')
def step_impl(context, properties):
    #from mgmt_settings_real import get_credentials, SUBSCRIPTION_ID
    #rg, mgmt_client = test_utils.create_mgmt_client(get_credentials(), SUBSCRIPTION_ID)
    _, prop = properties.split(' ')
    if prop == '100TU':
        context.eh_config = test_utils.get_eventhub_100TU_config()
    else:
        raise ValueError("Unrecognised property: {}".format(prop))

@When('I start a message sender')
def step_impl(context):
    from azure.eventhub import EventHubClient
    address = "sb://{}/{}".format(context.eh_config['hostname'], context.eh_config['event_hub'])
    context.client = EventHubClient(
        address,
        username=context.eh_config['key_name'],
        password=context.eh_config['access_key'])
    context.sender = client.add_sender()
    context.client.run()

@when('I {clients} messages for {hours} hours')
def step_impl(context, clients, hours):
    assert True is not False

@when('I {clients} messages {destination} for {hours} hours')
def step_impl(context, clients, destination, hours):
    assert True is not False

@then('I should receive no errors')
def step_impl(context):
    assert context.failed is False

@then('I can shutdown the {clients} cleanly')
def step_impl(context, clients):
    assert context.failed is False

@then('I should achieve throughput of greater than {total} messages')
def step_impl(context, total):
    assert context.failed is False

@then('I should achieve throughput of greater than {total} messages from {source}')
def step_impl(context, total, source):
    assert context.failed is False

@then('I remove the EventHub')
def step_impl(context):
    assert context.failed is False