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
import json
import logging
import os
import io
import uuid

from azure.purview.workflow import PurviewWorkflowClient
from azure.identity import UsernamePasswordCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the value of the endpoint as environment variables:
# WORKFLOW_ENDPOINT
# Set the values of client ID and tenant ID of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID
# set the values of username and password of the AAD user as environment variables:
# USERNAME, PASSWORD
try:
    endpoint = str(os.getenv("WORKFLOW_ENDPOINT"))
    client_id = str(os.getenv("AZURE_CLIENT_ID"))
    tenant_id = str(os.getenv("AZURE_TENANT_ID"))
    username = str(os.getenv("USERNAME"))
    password = str(os.getenv("PASSWORD"))
except KeyError:
    LOG.error(
        "Missing environment variable 'WORKFLOW_ENDPOINT' or 'AZURE_CLIENT_ID' or 'AZURE_TENANT_ID' or 'USERNAME' or "
        "'PASSWORD' - please set if before running the example")
    exit()
credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password,
                                        tenant_id=tenant_id)
# Build a client through AAD
client = PurviewWorkflowClient(endpoint=endpoint, credential=credential)

try:
    workflow_id = str(uuid.uuid4())
    workflow = {
      "name": "Create glossary term workflow",
      "description": "",
      "triggers": [
        {
          "type": "when_term_creation_is_requested",
          "underGlossaryHierarchy": "/glossaries/20031e20-b4df-4a66-a61d-1b0716f3fa48"
        }
      ],
      "isEnabled": True,
      "actionDag": {
        "actions": {
          "Start and wait for an approval": {
            "type": "Approval",
            "inputs": {
              "parameters": {
                "approvalType": "PendingOnAll",
                "title": "Approval Request for Create Glossary Term",
                "assignedTo": [
                  "eece94d9-0619-4669-bb8a-d6ecec5220bc"
                ]
              }
            },
            "runAfter": {}
          },
          "Condition": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@outputs('Start and wait for an approval')['body/outcome']",
                    "Approved"
                  ]
                }
              ]
            },
            "actions": {
              "Create glossary term": {
                "type": "CreateTerm",
                "runAfter": {}
              },
              "Send email notification": {
                "type": "EmailNotification",
                "inputs": {
                  "parameters": {
                    "emailSubject": "Glossary Term Create - APPROVED",
                    "emailMessage": "Your request for Glossary Term @{triggerBody()['request']['term']['name']} is approved.",
                    "emailRecipients": [
                      "@{triggerBody()['request']['requestor']}"
                    ]
                  }
                },
                "runAfter": {
                  "Create glossary term": [
                    "Succeeded"
                  ]
                }
              }
            },
            "else": {
              "actions": {
                "Send reject email notification": {
                  "type": "EmailNotification",
                  "inputs": {
                    "parameters": {
                      "emailSubject": "Glossary Term Create - REJECTED",
                      "emailMessage": "Your request for Glossary Term @{triggerBody()['request']['term']['name']} is rejected.",
                      "emailRecipients": [
                        "@{triggerBody()['request']['requestor']}"
                      ]
                    }
                  },
                  "runAfter": {}
                }
              }
            },
            "runAfter": {
              "Start and wait for an approval": [
                "Succeeded"
              ]
            }
          }
        }
      }
    }
    result = client.create_or_replace_workflow(workflow_id=workflow_id, workflow_create_or_update_command=workflow)
    print(result)
except HttpResponseError as e:
    print(f"Failed to send JSON message: {e}")
