# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_quantum_workspace.py
DESCRIPTION:
    This sample demonstrates creating a connnection with Azure Quantum by creating a
    Workspace.
USAGE:
    python sample_quantum_workspace.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_SUBSCRIPTION_ID - the identification string of your subscription
    2) AZURE_RESOURCE_GROUP - the resource group name under your subscription
    3) AZURE_WORKSPACE_NAME - the name of your quantum workspace
    4) AZURE_STORAGE - the blob service string of your storage account
"""

import os

from azure.quantum import Workspace

ws = Workspace(subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"), resource_group=os.getenv("AZURE_RESOURCE_GROUP"), name=os.getenv("AZURE_WORKSPACE_NAME"), storage=os.getenv("AZURE_STORAGE"))
ws.login()

