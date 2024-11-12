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
from ..events import cloudmachine_events
from .._resources import resources
from .._resources._client_settings import ClientSettings
from ._resource import (
    _UNSET,
    ExistingResource,
    CloudMachineId,
    ResourceGroup,
    ResourceName,
    SubscriptionResourceId,
    PrincipalId,
    ResourceId,
    _serialize_resource,
    generate_envvar
)
from ._roles import RoleAssignment, RoleAssignmentProperties
from ._identity import ManagedIdentity, UserAssignedIdentities
from .servicebus import (
    ServiceBusNamespace,
    ServiceBusRoleAssignments,
    AuthorizationRule,
    ServiceBusTopic,
    TopicSubsciprtion,
)
from .storage import (
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
from ._openai import CognitiveServices, AIRoleAssignments, AiDeployment
from ._search import SearchServices, SearchRoleAssignments


def azd_env_name(name: str, host: str, label: Optional[str]) -> str:
    suffix = 'local' if host == 'local' else label
    return f'cloudmachine-{name}' + (f'-{suffix}' if suffix else '')


def provision_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    args = ['azd', 'provision', '-e', project_name]
    print("Running: ", args)
    output = subprocess.run(args)
    print("Output: ", output)


def shutdown_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    args = ['azd', 'down', '-e', project_name, '--force', '--purge']
    print("Running: ", args)
    output = subprocess.run(args)
    print("Output: ", output)


def deploy_project(deployment: 'CloudMachineDeployment', label: Optional[str]) -> None:
    project_name = azd_env_name(deployment.name, deployment.host, label)
    args = ['azd', 'provision', '-e', project_name]
    print("Running: ", args)
    output = subprocess.run(args)
    print("Output: ", output)
    if output.returncode == 0:
        deployment_name = f"py-cloudmachine-{deployment.name}"
        args = ['azd', 'deploy', deployment_name, '-e', project_name]
        print("Running: ", args)
        output = subprocess.run(args)
        print("Output: ", output)
    else:
        print("Resource provision failed.")


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
    host: Union[Literal['local'], AppServicePlan]
    identity: ManagedIdentity
    storage: Optional[ClientSettings]
    messaging: Optional[ClientSettings]
    data: Optional[ClientSettings]
    openai: Optional[ClientSettings]
    documentai: Optional[ClientSettings]
    search: Optional[ClientSettings]
    app_settings: Dict[str, str]

    def __init__(
        self,
        *,
        name: str,
        location: Optional[str] = None,
        host: Literal['local', 'appservice', 'containerapp'] = 'local',
        events: bool = True,
        messaging: Union[bool, ServiceBusNamespace] = True,
        storage: Union[bool, StorageAccount] = True,
        openai: Union[bool, CognitiveServices] = False,
        documentai: Union[bool, CognitiveServices] = False,
        search: Union[bool, ClientSettings] = False,
        monitoring: bool = True,
        vault: bool = True,

    ) -> None:
        if not name or not (name.isalnum() and name[0].isalpha() and len(name) <= 25):
            raise ValueError("CloudMachine must have a valid name.")
        self.name = name.lower()
        self.location = location
        self.app_settings = {}

        self._params = copy.deepcopy(DEFAULT_PARAMS)
        self._core = ResourceGroup(
            friendly_name=self.name,
            tags={"abc": "def"},
        )
        self.identity = ManagedIdentity()
        self._core.add(self.identity)
        self.storage = None
        self.data = None
        if storage:
            self._storage_resource = self._define_storage(storage)
            self._core.add(self._storage_resource)
            if self._storage_resource.tables:
                self.data = resources.get('storage:table')
            self.storage = resources.get('storage:blob')['cloudmachine']
            self.storage.set('container_name', 'default')
        self.messaging = None
        if messaging:
            if isinstance(messaging, ClientSettings):
                self.messaging = messaging
                if 'default_topic' not in self.messaging:
                    self.messaging.set('default_topic', 'cm_default_topic')
                if 'default_subscription' not in self.messaging:
                    self.messaging.set('default_subscription', 'cm_default_subscription')
            else:
                self._messaging_resource = self._define_messaging()
                self._core.add(self._messaging_resource)
                self.messaging = resources.get('servicebus')['cloudmachine']
                self.messaging.set('default_topic', 'cm_default_topic')
                self.messaging.set('default_subscription', 'cm_default_subscription')
        if events and messaging:
            self._core.add(self._define_events())
        self.openai = None
        if openai:
            if isinstance(openai, ClientSettings):
                self.openai = openai
            else:
                self._openai_resource = self._define_ai()
                self._core.add(self._openai_resource)
                self.openai = resources.get('openai')['cloudmachine']
                self.openai.set('embeddings_model', 'embedding')
                self.openai.set('embeddings_deployment', 'text-embedding-ada-002')
                self.openai.set('embeddings_dimensions', 1536)
                self.openai.set('chat_model', 'gpt-35-turbo')
                self.openai.set('chat_deployment', 'chat')
        self.documentai = None
        if documentai:
            if isinstance(documentai, ClientSettings):
                self.documentai = documentai
                if not 'default_model' in self.documentai:
                    self.documentai.set('default_model', 'prebuilt-layout')
            else:
                self._docintelli_resource = self._define_docintelligence()
                self._core.add(self._docintelli_resource)
                self.documentai = resources.get('documentai')['cloudmachine']
                self.documentai.set('default_model', 'prebuilt-layout')
        self.search = None
        if search:
            if isinstance(search, ClientSettings):
                self.search = search
                if not 'document_embedding_index' in self.search:
                    self.search.set('document_embedding_index', 'documentembeddingindex')
            else:
                self._search_resource = self._define_search()
                self._core.add(self._search_resource)
                self.search = resources.get('search')['cloudmachine']
                self.search.set('document_embedding_index', 'documentembeddingindex')
                self.search.set('semantic_config', 'default')
                self.search.set('semantic_ranker', 'free')
                self.search.set('analyzer_name', 'en.microsoft')
                self.search.set('query_speller', 'lexicon')
                self.search.set('query_language', 'en-us')
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

    def _define_storage(self, storage: Union[bool, StorageAccount]) -> StorageAccount:
        sku = {'name': 'Standard_LRS'}
        containers = [Container(name="default")]
        blobs = BlobServices()
        tables = TableServices()
        properties = {
            'accessTier': 'Hot',
            'allowBlobPublicAccess': False,
            'isHnsEnabled': True
        }
        identity = {
            'type': 'UserAssigned',
            'userAssignedIdentities': UserAssignedIdentities((self.identity, {}))
        }
        roles = [
            RoleAssignment(
                properties={
                    'roleDefinitionId': SubscriptionResourceId(
                        'Microsoft.Authorization/roleDefinitions',
                        StorageRoleAssignments.BLOB_DATA_CONTRIBUTOR
                    ),
                    'principalId': PrincipalId(),
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
            ),
        ]
        if isinstance(storage, StorageAccount):
            sku = storage.sku if storage.sku is not _UNSET else sku
            blobs = storage.blobs if storage.blobs is not None else blobs
            blobs.containers = blobs.containers if blobs.containers else containers
            tables = storage.tables if storage.tables is not None else tables
            if storage.properties is not _UNSET:
                properties.update(storage.properties)
            identity = storage.identity if storage.identity is not _UNSET else identity
            roles = storage.roles if storage.roles else roles
        return StorageAccount(
            kind='StorageV2',
            sku=sku,
            blobs=blobs,
            tables=tables,
            properties=properties,
            identity=identity,
            roles=roles
        )

    def _define_events(self) -> ServiceBusNamespace:
        return SystemTopics(
            identity={
                'type': 'UserAssigned',
                'userAssignedIdentities': UserAssignedIdentities((self.identity, {}))
            },
            properties={
                'source': ResourceId(self._storage_resource),
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
                                'endpointType': 'ServiceBusTopic',
                                'properties': {
                                    'resourceId': ResourceId(self._messaging_resource.topics[0])
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
                    dependson=[self._messaging_resource.roles[1]]
                )
            ]
        )

    def _define_ai(self) -> CognitiveServices:
        return CognitiveServices(
            name=ResourceName("openai"),
            kind='OpenAI',
            properties={
                'customSubDomainName': CloudMachineId(),
                'publicNetworkAccess': 'Enabled',
                'disableLocalAuth': True
            },
            sku={
                'name': 'S0'
            },
            roles=[
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            AIRoleAssignments.OPENAI_CONTRIBUTOR
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                ),
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            AIRoleAssignments.OPENAI_USER
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'ServicePrincipal'
                    }
                )
            ],
            deployments=[
                AiDeployment(
                    name='chat',
                    properties={
                        'model': {
                            'format': 'OpenAI',
                            'name': 'gpt-35-turbo',
                            'version': '0125'  # 0613?
                        }
                    },
                    sku={
                        'name': 'Standard',
                        'capacity': 30
                    }
                ),
                AiDeployment(  # dimensions 1536
                    name='embedding',
                    properties={
                        'model': {
                            'format': 'OpenAI',
                            'name': 'text-embedding-ada-002',
                            'version': '2'
                        }
                    },
                    sku={
                        'name': 'Standard',
                        'capacity': 30
                    }
                )
            ]

        )

    def _define_docintelligence(self) -> CognitiveServices:
        return CognitiveServices(
            name=ResourceName('docsai'),
            kind='FormRecognizer',
            properties={
                'customSubDomainName': CloudMachineId(),
                'publicNetworkAccess': 'Enabled',
                'disableLocalAuth': True
            },
            sku={
                'name': 'S0'
            },
            roles=[
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            AIRoleAssignments.COGNITIVE_SERVICES_USER
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                )
            ],
            deployments=[
            ]

        )
    
    def _define_search(self) -> SearchServices:
        return SearchServices(
            sku={
                'name': 'basic'
            },
            properties={
                'disableLocalAuth': True,
                'publicNetworkAccess': 'enabled',
                'semanticSearch': 'free',
                'encryptionWithCmk': {
                    'enforcement': 'Unspecified'
                },
                'replicaCount': 1,
                'hostingMode': 'default'
            },
            roles=[
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            SearchRoleAssignments.SERVICE_CONTRIBUTOR
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                ),
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            SearchRoleAssignments.INDEX_DATA_CONTRIBUTOR
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
                ),
                RoleAssignment(
                    properties={
                        'roleDefinitionId': SubscriptionResourceId(
                            'Microsoft.Authorization/roleDefinitions',
                            SearchRoleAssignments.INDEX_DATA_READER
                        ),
                        'principalId': PrincipalId(),
                        'principalType': 'User'
                    }
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
                _serialize_resource(main, self._core)
                outputs = self._core.write(cm_file)
                if self.host != 'local':
                    self.app_settings.update({f"AZURE_CLOUDMACHINE_{generate_envvar(k)}": v for k, v in outputs.items()})
                    outputs.update(self.host.write(cm_file))

            main.write("module cloudmachine 'cloudmachine.bicep' = {\n")
            main.write("    name: 'cloudmachine'\n")
            main.write(f"    scope: {self._core._symbolicname}\n")
            main.write("    params: {\n")
            main.write("        location: location\n")
            main.write("        tags: tags\n")
            main.write("        principalId: principalId\n")
            main.write("        cloudmachineId: cloudmachineId\n")
            main.write("    }\n")
            main.write("}\n\n")
            for output in outputs.keys():
                main.write(f"output AZURE_CLOUDMACHINE_{generate_envvar(output)} string = cloudmachine.outputs.{output}\n")
            # for resource in self.ai:
            #     if isinstance(resource, ExistingResource):
            #         for output, value in resource.write().items():
            #             main.write(f"output AZURE_CLOUDMACHINE_{generate_envvar(output)} string = '{value}'\n")
            main.write(f"output AZURE_CLOUDMACHINE_RESOURCE_GROUP string = {self._core._symbolicname}.name")

        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            json.dump(self._params, params, indent=4)
