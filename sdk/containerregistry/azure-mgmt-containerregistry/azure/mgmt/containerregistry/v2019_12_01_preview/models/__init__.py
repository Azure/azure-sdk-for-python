# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models_py3 import (  # type: ignore
    Actor,
    CallbackConfig,
    EncryptionProperty,
    Event,
    EventContent,
    EventInfo,
    EventListResult,
    EventRequestMessage,
    EventResponseMessage,
    ExportPipeline,
    ExportPipelineListResult,
    ExportPipelineTargetProperties,
    IPRule,
    IdentityProperties,
    ImportImageParameters,
    ImportPipeline,
    ImportPipelineListResult,
    ImportPipelineSourceProperties,
    ImportSource,
    ImportSourceCredentials,
    KeyVaultProperties,
    NetworkRuleSet,
    OperationDefinition,
    OperationDisplayDefinition,
    OperationListResult,
    OperationLogSpecificationDefinition,
    OperationMetricSpecificationDefinition,
    OperationServiceSpecificationDefinition,
    PipelineRun,
    PipelineRunListResult,
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineRunSourceProperties,
    PipelineRunTargetProperties,
    PipelineSourceTriggerDescriptor,
    PipelineSourceTriggerProperties,
    PipelineTriggerDescriptor,
    PipelineTriggerProperties,
    Policies,
    PrivateEndpoint,
    PrivateEndpointConnection,
    PrivateEndpointConnectionListResult,
    PrivateLinkResource,
    PrivateLinkResourceListResult,
    PrivateLinkServiceConnectionState,
    ProgressProperties,
    ProxyResource,
    QuarantinePolicy,
    RegenerateCredentialParameters,
    Registry,
    RegistryListCredentialsResult,
    RegistryListResult,
    RegistryNameCheckRequest,
    RegistryNameStatus,
    RegistryPassword,
    RegistryUpdateParameters,
    RegistryUsage,
    RegistryUsageListResult,
    Replication,
    ReplicationListResult,
    ReplicationUpdateParameters,
    Request,
    Resource,
    RetentionPolicy,
    Sku,
    Source,
    Status,
    SystemData,
    Target,
    TrustPolicy,
    UserIdentityProperties,
    VirtualNetworkRule,
    Webhook,
    WebhookCreateParameters,
    WebhookListResult,
    WebhookUpdateParameters,
)

from ._container_registry_management_client_enums import (  # type: ignore
    Action,
    ActionsRequired,
    ConnectionStatus,
    CreatedByType,
    DefaultAction,
    EncryptionStatus,
    ImportMode,
    LastModifiedByType,
    NetworkRuleBypassOptions,
    PasswordName,
    PipelineOptions,
    PipelineRunSourceType,
    PipelineRunTargetType,
    PipelineSourceType,
    PolicyStatus,
    ProvisioningState,
    PublicNetworkAccess,
    RegistryUsageUnit,
    ResourceIdentityType,
    SkuName,
    SkuTier,
    TriggerStatus,
    TrustPolicyType,
    WebhookAction,
    WebhookStatus,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "Actor",
    "CallbackConfig",
    "EncryptionProperty",
    "Event",
    "EventContent",
    "EventInfo",
    "EventListResult",
    "EventRequestMessage",
    "EventResponseMessage",
    "ExportPipeline",
    "ExportPipelineListResult",
    "ExportPipelineTargetProperties",
    "IPRule",
    "IdentityProperties",
    "ImportImageParameters",
    "ImportPipeline",
    "ImportPipelineListResult",
    "ImportPipelineSourceProperties",
    "ImportSource",
    "ImportSourceCredentials",
    "KeyVaultProperties",
    "NetworkRuleSet",
    "OperationDefinition",
    "OperationDisplayDefinition",
    "OperationListResult",
    "OperationLogSpecificationDefinition",
    "OperationMetricSpecificationDefinition",
    "OperationServiceSpecificationDefinition",
    "PipelineRun",
    "PipelineRunListResult",
    "PipelineRunRequest",
    "PipelineRunResponse",
    "PipelineRunSourceProperties",
    "PipelineRunTargetProperties",
    "PipelineSourceTriggerDescriptor",
    "PipelineSourceTriggerProperties",
    "PipelineTriggerDescriptor",
    "PipelineTriggerProperties",
    "Policies",
    "PrivateEndpoint",
    "PrivateEndpointConnection",
    "PrivateEndpointConnectionListResult",
    "PrivateLinkResource",
    "PrivateLinkResourceListResult",
    "PrivateLinkServiceConnectionState",
    "ProgressProperties",
    "ProxyResource",
    "QuarantinePolicy",
    "RegenerateCredentialParameters",
    "Registry",
    "RegistryListCredentialsResult",
    "RegistryListResult",
    "RegistryNameCheckRequest",
    "RegistryNameStatus",
    "RegistryPassword",
    "RegistryUpdateParameters",
    "RegistryUsage",
    "RegistryUsageListResult",
    "Replication",
    "ReplicationListResult",
    "ReplicationUpdateParameters",
    "Request",
    "Resource",
    "RetentionPolicy",
    "Sku",
    "Source",
    "Status",
    "SystemData",
    "Target",
    "TrustPolicy",
    "UserIdentityProperties",
    "VirtualNetworkRule",
    "Webhook",
    "WebhookCreateParameters",
    "WebhookListResult",
    "WebhookUpdateParameters",
    "Action",
    "ActionsRequired",
    "ConnectionStatus",
    "CreatedByType",
    "DefaultAction",
    "EncryptionStatus",
    "ImportMode",
    "LastModifiedByType",
    "NetworkRuleBypassOptions",
    "PasswordName",
    "PipelineOptions",
    "PipelineRunSourceType",
    "PipelineRunTargetType",
    "PipelineSourceType",
    "PolicyStatus",
    "ProvisioningState",
    "PublicNetworkAccess",
    "RegistryUsageUnit",
    "ResourceIdentityType",
    "SkuName",
    "SkuTier",
    "TriggerStatus",
    "TrustPolicyType",
    "WebhookAction",
    "WebhookStatus",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
