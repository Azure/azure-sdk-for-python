# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import asyncio

from azure.developer.devcenter.aio import DevCenterClient
from azure.identity import DefaultAzureCredential
from datetime import timedelta

"""
FILE: dev_box_action_async_sample.py

DESCRIPTION:
    This sample demonstrates how to get, delay and skip a dev box action using python DevCenterClient. 
    For this sample, you must have a running dev box created from a pool with auto-stop enabled. More details  
    on how to configure auto-stop at https://learn.microsoft.com/azure/dev-box/how-to-configure-stop-schedule
    and sample on how to create a dev box at dev_box_create_sample.py in this folder

USAGE:
    python dev_box_action_async_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

async def dev_box_action_async():

    # Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
    # DEVCENTER_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
    try:
        endpoint = os.environ["DEVCENTER_ENDPOINT"]
    except KeyError:
        raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

    # Build a client through AAD
    client = DevCenterClient(endpoint, credential=DefaultAzureCredential())

    async with client:
        # List Dev Boxes
        dev_boxes = []
        async for dev_box in client.list_all_dev_boxes_by_user("me"):
            dev_boxes.append(dev_box)
        if dev_boxes:
            print("List of dev boxes: ")
            for dev_box in dev_boxes:
                print(f"{dev_box.name}")

            # Select first dev box in the list
            target_dev_box = dev_boxes[0]
        else:
            raise ValueError("Missing Dev Box - please create one before running the example.")

        # Get the schedule default action. This action should exist for dev boxes created with auto-stop enabled
        action = await client.get_dev_box_action(target_dev_box.project_name, "me", target_dev_box.name, "schedule-default")
        next_action_time = action.next.scheduled_time
        print(f"\nAction {action.Name} is schedule to {action.ActionType} at {next_action_time}.")

        # Delay the action in 1hr
        delay_until = next_action_time + timedelta(hours=1)
        delayed_action = await client.delay_dev_box_action(
            target_dev_box.project_name, "me", target_dev_box.name, action.name, delay_until=delay_until
        )
        print(
            f"\nAction {delayed_action.Name} has been delayed and is now schedule to {delayed_action.ActionType} at {delayed_action.NextAction.ScheduledTime}."
        )

        # Skip the default schedule action
        await client.skip_dev_box_action(target_dev_box.project_name, "me", target_dev_box.name, "schedule-default")
        print(f"\nThe scheduled auto-stop action in dev box {target_dev_box.name} has been skipped")

async def main():
    await dev_box_action_async()

if __name__ == '__main__':
    asyncio.run(main())
