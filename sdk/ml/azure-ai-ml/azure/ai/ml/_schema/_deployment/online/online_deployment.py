# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointComputeType
from azure.ai.ml._schema._deployment.deployment import DeploymentSchema
from azure.ai.ml._schema._utils.utils import exit_if_registry_assets
from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PublicNetworkAccess
from azure.ai.ml._schema.job.creation_context import CreationContextSchema

from .data_collector_schema import DataCollectorSchema
from .liveness_probe import LivenessProbeSchema
from .request_settings_schema import RequestSettingsSchema
from .resource_requirements_schema import ResourceRequirementsSchema
from .scale_settings_schema import DefaultScaleSettingsSchema, TargetUtilizationScaleSettingsSchema

module_logger = logging.getLogger(__name__)


class OnlineDeploymentSchema(DeploymentSchema):
    app_insights_enabled = fields.Bool()
    scale_settings = UnionField(
        [
            NestedField(DefaultScaleSettingsSchema),
            NestedField(TargetUtilizationScaleSettingsSchema),
        ]
    )
    request_settings = NestedField(RequestSettingsSchema)
    liveness_probe = NestedField(LivenessProbeSchema)
    readiness_probe = NestedField(LivenessProbeSchema)
    provisioning_state = fields.Str()
    instance_count = fields.Int()
    type = StringTransformedEnum(
        required=False,
        allowed_values=[
            EndpointComputeType.MANAGED.value,  # pylint: disable=no-member
            EndpointComputeType.KUBERNETES.value,  # pylint: disable=no-member
        ],
        casing_transform=camel_to_snake,
    )
    model_mount_path = fields.Str()
    instance_type = fields.Str()
    data_collector = ExperimentalField(NestedField(DataCollectorSchema))


class KubernetesOnlineDeploymentSchema(OnlineDeploymentSchema):
    resources = NestedField(ResourceRequirementsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import KubernetesOnlineDeployment

        exit_if_registry_assets(data=data, caller="K8SDeployment")
        return KubernetesOnlineDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class ManagedOnlineDeploymentSchema(OnlineDeploymentSchema):
    instance_type = fields.Str(required=True)
    egress_public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.ENABLED, PublicNetworkAccess.DISABLED]
    )
    private_network_connection = ExperimentalField(fields.Bool())
    data_collector = NestedField(DataCollectorSchema)
    creation_context = NestedField(CreationContextSchema, dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ManagedOnlineDeployment

        return ManagedOnlineDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
