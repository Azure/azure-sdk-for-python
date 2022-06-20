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
import logging
import os

from azure.analytics.loadtestservice import LoadTestClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, LOADTESTSERVICE_ENDPOINT
try:
    endpoint = os.environ["LOADTESTSERVICE_ENDPOINT"]
except KeyError:
    LOG.error("Missing environment variable 'LOADTESTSERVICE_ENDPOINT' - please set if before running the example")
    exit()

# Build a client through AAD
client = LoadTestClient(credential=DefaultAzureCredential(), endpoint=endpoint)

# Creating or updating a load test
try:
    test_id="test-name"
    body_test={"createdBy": "user-name",  # Optional. The user that created the test model.
        "createdDateTime": "2022-06-20 00:00:00",  # Optional. The created
        "description": "test-description",  # Optional. The test description.
        "displayName": "test-display-name",  # Optional. Display name of a test.
        "resourceId": "resource-ID",  # Optional. 
        # more param can be there
        }  
    result = client.test.create_or_update_test(test_id, body_test)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

#Uploading a test file
try:
    test_id="test-name"
    file_id="file-name"
    file_body = {}
    #reading file using python open
    f= open("jmx-script.jmx","rb")
    file_body["file"]=f 
    result=client.test.upload_test_file(test_id,file_id,file_body)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

#Creating a test run
try:
    test_run_id="test-run-name"
    body_test_run=body_test={"createdBy": "user-name",  # Optional. The user that created the test model.
        "createdDateTime": "2022-06-20 00:00:00",  # Optional. The created
        "description": "test-description",  # Optional. The test description.
        "displayName": "test-display-name",  # Optional. Display name of a test.
        "resourceId": "resource-ID",  # Optional. 
        # more param can be there
        } 
    result=client.test_run.create_and_update_test(test_run_id,body_test_run)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Getting test run client metrics
try:
    test_run_id="test-run-name"
    body_test_run=body_test={"createdBy": "user-name",  # Optional. The user that created the test model.
        "createdDateTime": "2022-06-20 00:00:00",  # Optional. The created
        "description": "test-description",  # Optional. The test description.
        "displayName": "test-display-name",  # Optional. Display name of a test.
        "resourceId": "resource-ID",  # Optional. 
        # more param can be there
        } 
    result=client.test_run.get_test_run_client_metrics(test_run_id,body_test_run)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))


# Stopping a test run
try:
    test_run_id="test-run-name"
    result=client.test_run.stop_test_run(test_run_id)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Deleting a load test
try:
    test_id="test-name"
    result=client.test.delete_load_test(test_id)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))