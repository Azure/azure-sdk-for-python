# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_deployment_template.py
DESCRIPTION:
    These samples configures some operations of the deployment template
USAGE:
    python ml_samples_deployment_template.py
"""

import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
    resource_group=os.environ["RESOURCE_GROUP_NAME"],
    registry_name="test-reg",
)

print(ml_client)

# Create a deployment template
ml_client.deployment_templates.create_or_update(
    "C:/Projects/azure-sdk-for-python/sdk/ml/azure-ai-ml/samples/deployment-template-schema.yaml"
)

# List all deployment templates
templates = ml_client.deployment_templates.list()
print(templates)

for temp in templates:
    print(temp)

# Get a specific template
template = ml_client.deployment_templates.get(name="DT03", version="1")
print(template)

# Update a Deployment Template
# only Description and tags can be updated
template.description = "Updated Description"
template.tags = {"key": "value"}
ml_client.deployment_templates.create_or_update(template)

# Archive a deployment template
ml_client.deployment_templates.archive(name="DT10", version="1")

# Restore a deployment template
ml_client.deployment_templates.restore(name="DT10", version="1")
