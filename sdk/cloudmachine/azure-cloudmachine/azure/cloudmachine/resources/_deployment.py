# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

import json
import os
import shutil
import copy
import subprocess
from typing import Dict, Literal, Optional, List, Union

from .._version import VERSION
from ._resource import (
    ResourceGroup,
    SubscriptionResourceId,
    PrincipalId,
    ResourceId,
    _serialize_resource,
    generate_envvar
)
from ._roles import RoleAssignment, RoleAssignmentProperties
from ._identity import ManagedIdentity, UserAssignedIdentities
from ._servicebus import (
    ServiceBusNamespace,
    ServiceBusRoleAssignments,
    AuthorizationRule,
    ServiceBusTopic,
    TopicSubsciprtion,
)
from ._storage import (
    Container,
    StorageAccount,
    BlobServices,
    StorageRoleAssignments,
    TableServices
)
from ._eventgrid import (
    EventSubscription,
    SystemTopics,
)
from ._appservice import (
    AppServiceAppSettingsConfig,
    AppServiceLogsConfig,
    AppServicePlan,
    AppServiceSite,
    BasicPublishingCredentialsPolicy,
)
from .._httpclient._eventlistener import cloudmachine_events


def azd_env_name(name: str, host: str, label: Optional[str]) -> str:
    suffix = 'local' if host == 'local' else label
    return f'cloudmachine-{name}' + (f'-{suffix}' if suffix else '')


def run_project(deployment: 'CloudMachineDeployment', label: Optional[str], args: List[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    output = subprocess.run(['azd', 'provision', '-e', project_name])
    print(output)
    try:
        output = subprocess.run(args)
    except KeyboardInterrupt:
        return


def shutdown_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    output = subprocess.run(['azd', 'down', '-e', project_name, '--force', '--purge'])
    print(output)


def deploy_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    output = subprocess.run(['azd', 'provision', '-e', project_name])
    if output.returncode == 0:
        deployment_name = f"py-cloudmachine-{deployment.name}"
        output = subprocess.run(['azd', 'deploy', deployment_name, '-e', project_name])
    print(output)


def init_project(
        root_path: str,
        deployment: 'CloudMachineDeployment',
        label: Optional[str],
        metadata: Optional[Dict[str, str]] = None
) -> None:
    azure_dir = os.path.join(root_path, ".azure")
    azure_yaml = os.path.join(root_path, "azure.yaml")
    project_name = azd_env_name(deployment.name, deployment.host, label)
    project_dir = os.path.join(azure_dir, project_name)
    # TODO proper yaml parsing
    # Needs to properly set code root
    # Shouldn't overwrite on every run
    with open(azure_yaml, 'w') as config:
        config.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json\n\n")
        config.write(f"name: {deployment.name}\n")
        config.write("metadata:\n")
        config.write(f"  cloudmachine: {VERSION}\n")
        if metadata:
            for key, value in metadata.items():
                config.write(f"  {key}: {value}\n")
        config.write("infra:\n")
        config.write("  path: .infra\n\n")
        if isinstance(deployment.host, AppServicePlan):
            config.write("services:\n")
            config.write(f"  py-cloudmachine-{deployment.name}:\n")
            config.write("    project: .\n")
            config.write("    language: py\n")
            config.write("    host: appservice\n\n")

    if not os.path.isdir(azure_dir) or not os.path.isdir(project_dir):
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
    core: ResourceGroup
    host: Union[Literal['local'], AppServicePlan]
    identity: ManagedIdentity
    storage: Optional[StorageAccount] = None
    messaging: Optional[ServiceBusNamespace] = None
    app_settings: Dict[str, str]

    def __init__(
        self,
        *,
        name: str,
        location: Optional[str] = None,
        host: Literal['local', 'appservice', 'containerapp'] = 'local',
        events: bool = True,
        messaging: bool = True,
        storage: bool = True,
        monitoring: bool = True,
        vault: bool = True,

    ) -> None:
        if not name or not (name.isalnum() and name[0].isalpha() and len(name) <= 25):
            raise ValueError("CloudMachine must have a valid name.")
        self.name = name.lower()
        self.location = location
        self.app_settings = {}

        self._params = copy.deepcopy(DEFAULT_PARAMS)
        self.core = ResourceGroup(
            friendly_name=self.name,
            tags={"abc": "def"},
        )
        self.identity = ManagedIdentity()
        self.core.add(self.identity)
        if storage:
            self.storage = self._define_storage()
            self.core.add(self.storage)
        if messaging:
            self.messaging = self._define_messaging()
            self.core.add(self.messaging)
        if events and messaging:
            self.core.add(self._define_events())
        self.host = self._define_host(host)

    def _define_host(self, host: str) -> Union[str, AppServicePlan]:
        if host == 'local':
            return host
        if host == 'appservice':
            self.app_settings.update({
                'SCM_DO_BUILD_DURING_DEPLOYMENT': 'true',
                'ENABLE_ORYX_BUILD': 'true',
                'PYTHON_ENABLE_GUNICORN_MULTIWORKERS': 'true',
            })
            service_plan = AppServicePlan(
                kind='linux',
                sku={'name': 'B1', 'capacity': 1},
                properties={'reserved': True}
            )
            settings = AppServiceAppSettingsConfig(
                properties=self.app_settings
            )
            site = AppServiceSite(
                    kind='app,linux',
                    tags={'azd-service-name': 'py-cloudmachine-' + self.name},
                    identity={
                        'type': 'UserAssigned',
                        'userAssignedIdentities': UserAssignedIdentities((self.identity, {}))
                    },
                    properties={
                        'serverFarmId': ResourceId(service_plan),
                        'httpsOnly': True,
                        'clientAffinityEnabled': False,
                        'siteConfig': {
                            'minTlsVersion': '1.2',
                            'use32BitWorkerProcess': False,
                            'alwaysOn': True,
                            'ftpsState': 'FtpsOnly',
                            'linuxFxVersion': 'python|3.12',
                            'cors': {
                                'allowedOrigins': ['https://portal.azure.com', 'https://ms.portal.azure.com']
                            }
                        }
                    },
                    configs=[
                        settings,
                        AppServiceLogsConfig(
                            properties={
                                'applicationLogs': {
                                    'fileSystem': {'level': 'Verbose'}
                                },
                                'detailedErrorMessages': {'enabled': True},
                                'failedRequestsTracing': {'enabled': True},
                                'httpLogs': {
                                    'fileSystem': {'enabled':True, 'retentionInDays': 1, 'retentionInMb': 35}
                                }
                            },
                            dependson=[settings],
                        )
                    ],
                    policies=[
                        BasicPublishingCredentialsPolicy(
                            name='ftp',
                            properties={'allow': False}
                        ),
                        BasicPublishingCredentialsPolicy(
                            name='scm',
                            properties={'allow': False}
                        )
                    ],
                )
            service_plan.site = site
            return service_plan
        raise ValueError("Unexpected value for host.")

    def _define_messaging(self) -> ServiceBusNamespace:
        return ServiceBusNamespace(
            sku={
                'name': 'Standard',
                'tier': 'Standard'
            },
            roles=[
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            ServiceBusRoleAssignments.DATA_OWNER
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                ),
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            ServiceBusRoleAssignments.DATA_SENDER
                        ),
                        'principalId': PrincipalId(self.identity),
                        'principalType': 'ServicePrincipal'
                    }
                )
            ],
            auth_rules=[
                AuthorizationRule(
                    properties={'rights': ['Listen', 'Send', 'Manage']}
                )
            ],
            topics=[
                ServiceBusTopic(
                    name="cm_internal_topic",
                    properties={
                        'defaultMessageTimeToLive': 'P14D',
                        'enableBatchedOperations': True,
                        'maxMessageSizeInKilobytes': 256,
                        'requiresDuplicateDetection': False,
                        'status': 'Active',
                        'supportOrdering': True
                    },
                    subscriptions=[
                        TopicSubsciprtion(
                            name="cm_internal_subscription",
                            properties={
                                'deadLetteringOnFilterEvaluationExceptions': True,
                                'deadLetteringOnMessageExpiration': True,
                                'defaultMessageTimeToLive': 'P14D',
                                'enableBatchedOperations': True,
                                'isClientAffine': False,
                                'lockDuration': 'PT30S',
                                'maxDeliveryCount': 10,
                                'requiresSession': False,
                                'status': 'Active'
                            }
                        )
                    ]
                ),
                ServiceBusTopic(
                    name="cm_default_topic",
                    properties={
                        'defaultMessageTimeToLive': 'P14D',
                        'enableBatchedOperations': True,
                        'maxMessageSizeInKilobytes': 256,
                        'requiresDuplicateDetection': False,
                        'status': 'Active',
                        'supportOrdering': True
                    },
                    subscriptions=[
                        TopicSubsciprtion(
                            name="cm_default_subscription",
                            properties={
                                'deadLetteringOnFilterEvaluationExceptions': True,
                                'deadLetteringOnMessageExpiration': True,
                                'defaultMessageTimeToLive': 'P14D',
                                'enableBatchedOperations': True,
                                'isClientAffine': False,
                                'lockDuration': 'PT30S',
                                'maxDeliveryCount': 10,
                                'requiresSession': False,
                                'status': 'Active'
                            }
                        )
                    ]
                )
            ]
        )

    def _define_storage(self) -> StorageAccount:
        return StorageAccount(
            kind='StorageV2',
            sku={'name': 'Standard_LRS'},
            blobs=BlobServices(
                containers=[
                    Container(name="default")
                ]
            ),
            tables=TableServices(),
            properties={
                'accessTier': 'Hot',
                'allowBlobPublicAccess': False,
                'isHnsEnabled': True
            },
            identity={
                'type': 'UserAssigned',
                'userAssignedIdentities': UserAssignedIdentities((self.identity, {}))
            },
            roles=[
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            StorageRoleAssignments.BLOB_DATA_CONTRIBUTOR
                        ),
                        'principal_id': PrincipalId(),
                        'principalType': 'User'
                    }
                ),
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            StorageRoleAssignments.TABLE_DATA_CONTRIBUTOR
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                )
            ]
        )

    def _define_events(self) -> ServiceBusNamespace:
        return SystemTopics(
            identity={
                'type': 'UserAssigned',
                'userAssignedIdentities': UserAssignedIdentities((self.identity, {}))
            },
            properties={
                'source': ResourceId(self.storage),
                'topicType': 'Microsoft.Storage.StorageAccounts'
            },
            subscriptions=[
                EventSubscription(
                    properties={
                        'deliveryWithResourceIdentity': {
                            'identity': {
                                'type': 'UserAssigned',
                                'userAssignedIdentity': ResourceId(self.identity)
                            },
                            'destination': {
                                'properties': {
                                    'resourceId': ResourceId(self.messaging.topics[0])
                                }
                            }
                        },
                        'eventDeliverySchema': 'EventGridSchema',
                        'filter': {
                            'includedEventTypes': list(cloudmachine_events.keys()),
                            'enableAdvancedFilteringOnArrays': True
                        },
                        'retryPolicy': {
                            'maxDeliveryAttempts': 30,
                            'eventTimeToLiveInMinutes': 1440
                        }
                    },
                    dependson=[self.messaging.roles[1]]
                )
            ]
        )

    def write(self, root_path: str):
        infra_dir = _get_empty_directory(root_path, ".infra")
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
            cm_bicep = os.path.join(infra_dir, "cloudmachine.bicep")
            with open(cm_bicep, 'w') as cm_file:
                _serialize_resource(main, self.core)
                outputs = self.core.write(cm_file)
                if self.host != 'local':
                    self.app_settings.update({f"AZURE_CLOUDMACHINE_{generate_envvar(k)}": v for k, v in outputs.items()})
                    outputs.update(self.host.write(cm_file))

            main.write("module cloudmachine 'cloudmachine.bicep' = {\n")
            main.write("    name: 'cloudmachine'\n")
            main.write(f"    scope: {self.core._symbolicname}\n")
            main.write("    params: {\n")
            main.write("        location: location\n")
            main.write("        tags: tags\n")
            main.write("        principalId: principalId\n")
            main.write("        cloudmachineId: cloudmachineId\n")
            main.write("    }\n")
            main.write("}\n\n")
            for output in outputs.keys():
                main.write(f"output AZURE_CLOUDMACHINE_{generate_envvar(output)} string = cloudmachine.outputs.{output}\n")


        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            json.dump(self._params, params, indent=4)
