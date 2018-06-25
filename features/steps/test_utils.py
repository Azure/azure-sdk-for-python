# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

def create_mgmt_client(credentials, subscription, location='westus'):
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.eventhub import EventHubManagementClient

    resource_client = ResourceManagementClient(credentials, subscription)
    rg_name = 'pytest-{}'.format(uuid.uuid4())
    resource_group = resource_client.resource_groups.create_or_update(
                rg_name, {'location': location})

    eh_client = EventHubManagementClient(credentials, subscription)
    namespace = 'pytest-{}'.format(uuid.uuid4())
    creator = eh_client.namespaces.create_or_update(
        resource_group.name,
        namespace)
    create.wait()
    return resource_group, eh_client


def get_eventhub_config():
    config = {}
    config['hostname'] = os.environ['EVENT_HUB_HOSTNAME']
    config['event_hub'] = os.environ['EVENT_HUB_NAME']
    config['key_name'] = os.environ['EVENT_HUB_SAS_POLICY']
    config['access_key'] = os.environ['EVENT_HUB_SAS_KEY']
    config['consumer_group'] = "$Default"
    config['partition'] = "0"
    return config
