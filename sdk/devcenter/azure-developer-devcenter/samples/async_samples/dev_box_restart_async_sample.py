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
from azure.developer.devcenter.models import PowerState
from azure.identity import DefaultAzureCredential

"""
FILE: dev_box_restart_async_sample.py

DESCRIPTION:
    This sample demonstrates how to restart, stop and start a dev box using python DevCenterClient. 
    For this sample, you must have a running dev box. More details on how to create a dev box 
    at dev_box_create_sample.py sample in this folder

USAGE:
    python devbox_restart_async_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

async def dev_box_restart_stop_start_async():

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
    
        # Get the target dev box properties
        project_name = target_dev_box.project_name
        user = target_dev_box.user
        dev_box_name = target_dev_box.name
    
        # Stop dev box if it's running
        if target_dev_box.power_state == PowerState.Running:
            stop_poller = await client.begin_stop_dev_box(project_name, user, dev_box_name)
            stop_result = await stop_poller.result()
            print(f"Stopping dev box completed with status {stop_result.status}")
    
        # At this point we should have a stopped dev box . Let's start it
        start_poller = await client.begin_start_dev_box(project_name, user, dev_box_name)
        start_result = await start_poller.result()
        print(f"Starting dev box completed with status {start_result.status}")
    
        # Restart the dev box
        restart_poller = await client.begin_restart_dev_box(project_name, user, dev_box_name)
        restart_result = await restart_poller.result()
        print(f"Done restarting the dev box with status {start_result.status}")

async def main():
    await dev_box_restart_stop_start_async()

if __name__ == '__main__':
    asyncio.run(main())
