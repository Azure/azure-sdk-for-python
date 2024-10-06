# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import shutil
import copy
import os
import subprocess
from typing import Literal, Optional, List

from ._resource import ResourceGroup, SubscriptionResourceId, PrincipalId, ResourceId
from .roles import RoleAssignment, RoleAssignmentProperties
from .identity import ManagedIdentity, UserAssignedIdentities
from .servicebus import (
    ServiceBusNamespace,
    ServiceBusSku,
    ServiceBusRoleAssignments,
    AuthorizationRule,
    AuthorizationRuleProperties,
    ServiceBusTopic,
    TopicProperties,
    TopicSubsciprtion,
    SubscriptionProperties
)
from .storage import (
    Container,
    StorageAccount,
    Sku,
    BlobServices,
    Properties,
    Identity,
    StorageRoleAssignments,
    Table,
    TableServices
)
from .eventgrid import (
    EventSubscription,
    SystemTopics,
    SystemTopicProperties,
    EventSubscriptionProperties,
    EventSubscriptionIdentity,
    EventSubscriptionFilter,
    IdentityInfo,
    DeliveryWithResourceIdentity,
    ServiceBusTopicEventSubscriptionDestination,
    ServiceBusTopicEventSubscriptionDestinationProperties,
    RetryPolicy
)


def azd_env_name(name: str, host: str, label: Optional[str]) -> str:
    suffix = 'local' if host == 'local' else label
    return f'cloudmachine-{name}' + (f'-{suffix}' if suffix else '')


def run_project(deployment: 'CloudMachineDeployment', label: Optional[str], args: List[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    output = subprocess.run(['azd', 'provision', '-e', project_name])
    print(output)
    args.append("run")
    try:
        output = subprocess.run(args)
    except KeyboardInterrupt:
        return


def shutdown_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    output = subprocess.run(['azd', 'down', '-e', project_name, '--force', '--purge'])
    print(output)


def init_project(root_path: str, deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    azure_dir = os.path.join(root_path, ".azure")
    azure_yaml = os.path.join(root_path, "azure.yaml")
    project_name = azd_env_name(deployment.name, deployment.host, label)
    if not os.path.isdir(azure_dir):
        print("No azure environments found. Building...")
        if not os.path.isfile(azure_yaml):
            print(f"No azure config found, building: {azure_yaml}.")
            with open(azure_yaml, 'w') as config:
                #TODO update config according to name and host.
                config.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json\n\n")
                config.write(f"name: {deployment.name}\n\n")
        print(f"Adding environment: {project_name}.")
        output = subprocess.run(['azd', 'env', 'new', project_name])
        print(output)
    if deployment.location:
        output = subprocess.run(['azd', 'env', 'set', 'AZURE_LOCATION', deployment.location, '-e', project_name])
        print(output)
    print("Finished environment setup.")


DEFAULT_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "environmentName": {
            "value": "${AZURE_ENV_NAME}"
        },
        "principalId": {
            "value": "${AZURE_PRINCIPAL_ID}"
        },
        "location": {
            "value": "${AZURE_LOCATION}"
        }
    }
}


def _get_empty_directory(root_path: str, name: str) -> str:
    new_dir = os.path.join(root_path, name)
    try:
        shutil.rmtree(new_dir)
    except FileNotFoundError:
        pass
    os.makedirs(new_dir)

    return new_dir


class CloudMachineDeployment:
    name: str
    location: Optional[str]
    groups: List[ResourceGroup]
    host: str

    def __init__(
        self,
        *,
        name: str,
        location: Optional[str] = None,
        host: Literal['local', 'appservice', 'containerapp'] = 'local',
    ) -> None:
        if not name:
            raise ValueError("CloudMachine must have a valid name.")
        self.name = name.lower()
        self.location = location
        self.host = host
        self._params = copy.deepcopy(DEFAULT_PARAMS)
        #if self.location:
        #    self._params["parameters"]["location"]["value"] = f"${{AZURE_LOCATION={self.location}}}"
        rg = ResourceGroup(
            friendly_name=self.name,
            tags={"abc": "def"},
        )
        self._identity = ManagedIdentity()
        rg.add(self._identity)
        self._storage = self._define_storage()
        rg.add(self._storage)
        self._messaging = self._define_messaging()
        rg.add(self._messaging)
        rg.add(self._define_events())
        self.groups = [rg]

    def _define_messaging(self) -> ServiceBusNamespace:
        return ServiceBusNamespace(
            sku=ServiceBusSku(
                name='Standard',
                tier='Standard'
            ),
            roles=[
                RoleAssignment(
                    properties=RoleAssignmentProperties(
                        role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', ServiceBusRoleAssignments.DATA_OWNER),
                        principal_id=PrincipalId(),
                        principal_type="User"
                    )
                ),
                RoleAssignment(
                    properties=RoleAssignmentProperties(
                        role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', ServiceBusRoleAssignments.DATA_SENDER),
                        principal_id=PrincipalId(self._identity),
                        principal_type="ServicePrincipal"
                    )
                )
            ],
            auth_rules=[
                AuthorizationRule(
                    properties=AuthorizationRuleProperties(
                        rights=['Listen', 'Send', 'Manage']
                    )
                )
            ],
            topics=[
                ServiceBusTopic(
                    name="cm_internal_topic",
                    properties=TopicProperties(
                        default_message_time_to_live='P14D',
                        enable_batched_operations=True,
                        max_message_size_in_kilobytes=256,
                        requires_duplicate_detection=False,
                        status='Active',
                        support_ordering=True
                    ),
                    subscriptions=[
                        TopicSubsciprtion(
                            name="cm_internal_subscription",
                            properties=SubscriptionProperties(
                                dead_lettering_on_filter_evaluation_exceptions=True,
                                dead_lettering_on_message_expiration=True,
                                default_message_time_to_live='P14D',
                                enable_batched_operations=True,
                                is_client_affine=False,
                                lock_duration='PT30S',
                                max_delivery_count=10,
                                requires_session=False,
                                status='Active'
                            )
                        )
                    ]
                ),
                ServiceBusTopic(
                    name="cm_default_topic",
                    properties=TopicProperties(
                        default_message_time_to_live='P14D',
                        enable_batched_operations=True,
                        max_message_size_in_kilobytes=256,
                        requires_duplicate_detection=False,
                        status='Active',
                        support_ordering=True
                    ),
                    subscriptions=[
                        TopicSubsciprtion(
                            name="cm_default_subscription",
                            properties=SubscriptionProperties(
                                dead_lettering_on_filter_evaluation_exceptions=True,
                                dead_lettering_on_message_expiration=True,
                                default_message_time_to_live='P14D',
                                enable_batched_operations=True,
                                is_client_affine=False,
                                lock_duration='PT30S',
                                max_delivery_count=10,
                                requires_session=False,
                                status='Active'
                            )
                        )
                    ]
                )
            ]
        )

    def _define_storage(self) -> StorageAccount:
        return StorageAccount(
            kind='StorageV2',
            sku=Sku(name='Standard_LRS'),
            blobs=BlobServices(
                containers=[
                    Container(name="default")
                ]
            ),
            tables=TableServices(
                tables=[
                    Table(name="default")
                ]
            ),
            properties=Properties(
                access_tier="Hot",
                allow_blob_public_access=False,
                is_hns_enabled=True
            ),
            identity=Identity(
                type='UserAssigned',
                user_assigned_identities=UserAssignedIdentities((self._identity, {}))),
            roles=[
                RoleAssignment(
                    properties=RoleAssignmentProperties(
                        role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', StorageRoleAssignments.BLOB_DATA_CONTRIBUTOR),
                        principal_id=PrincipalId(),
                        principal_type="User"
                    )
                ),
                RoleAssignment(
                    properties=RoleAssignmentProperties(
                        role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', StorageRoleAssignments.TABLE_DATA_CONTRIBUTOR),
                        principal_id=PrincipalId(),
                        principal_type="User"
                    )
                )
            ]
        )

    def _define_events(self) -> ServiceBusNamespace:
        return SystemTopics(
            identity=IdentityInfo(
                type="UserAssigned",
                user_assigned_identities=UserAssignedIdentities((self._identity, {}))
            ),
            properties=SystemTopicProperties(
                source=ResourceId(self._storage),
                topic_type='Microsoft.Storage.StorageAccounts'
            ),
            subscriptions=[
                EventSubscription(
                    properties=EventSubscriptionProperties(
                        delivery_with_resource_identity=DeliveryWithResourceIdentity(
                            identity=EventSubscriptionIdentity(
                                type="UserAssigned",
                                user_assigned_identity=ResourceId(self._identity)
                            ),
                            destination=ServiceBusTopicEventSubscriptionDestination(
                                properties=ServiceBusTopicEventSubscriptionDestinationProperties(
                                    resource_id=ResourceId(self._messaging.topics[0])
                                )
                            )
                        ),
                        event_delivery_schema='EventGridSchema',
                        filter=EventSubscriptionFilter(
                            included_event_types=[
                                'Microsoft.Storage.BlobCreated',
                                'Microsoft.Storage.BlobDeleted',
                                'Microsoft.Storage.BlobRenamed',
                            ],
                            enable_advanced_filtering_on_arrays=True
                        ),
                        retry_policy=RetryPolicy(
                            max_delivery_attempts=30,
                            event_time_to_live_in_minutes=1440
                        )
                    )
                )
            ]
        )

    def write(self, root_path: str):
        infra_dir = _get_empty_directory(root_path, "infra")
        main_bicep = os.path.join(infra_dir, "main.bicep")
        with open(main_bicep, 'w') as main:
            main.write("targetScope = 'subscription'\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('AZD environment name')\n")
            main.write("param environmentName string\n\n")
            main.write("@description('Id of the user or app to assign application roles')\n")
            main.write("param principalId string\n\n")
            main.write("@minLength(1)\n")
            main.write("@description('Primary location for all resources')\n")
            main.write("param location string\n\n")
            main.write("var tags = { 'azd-env-name': environmentName }\n")
            main.write("var cloudmachineId = uniqueString(subscription().subscriptionId, environmentName, location)\n\n")

            for rg in self.groups:
                rg.write(main)
        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            json.dump(self._params, params, indent=4)
