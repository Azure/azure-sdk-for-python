# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointComputeType
from azure.ai.ml._schema.core.fields import UnionField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import fields, post_load
from azure.ai.ml._schema import NestedField
from .scale_settings_schema import DefaultScaleSettingsSchema, TargetUtilizationScaleSettingsSchema
from .request_settings_schema import RequestSettingsSchema
from .resource_requirements_schema import ResourceRequirementsSchema
from .liveness_probe import LivenessProbeSchema
from azure.ai.ml._schema._deployment.deployment import DeploymentSchema
from azure.ai.ml._schema import ExperimentalField
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, PublicNetworkAccess

module_logger = logging.getLogger(__name__)


class OnlineDeploymentSchema(DeploymentSchema):
    app_insights_enabled = fields.Bool()
    scale_settings = UnionField(
        [NestedField(DefaultScaleSettingsSchema), NestedField(TargetUtilizationScaleSettingsSchema)]
    )
    request_settings = NestedField(RequestSettingsSchema)
    liveness_probe = NestedField(LivenessProbeSchema)
    readiness_probe = NestedField(LivenessProbeSchema)
    provisioning_state = fields.Str()
    instance_count = fields.Int()
    type = StringTransformedEnum(
        required=False,
        allowed_values=[EndpointComputeType.MANAGED.value, EndpointComputeType.KUBERNETES.value],
        casing_transform=camel_to_snake,
    )
    model_mount_path = fields.Str()
    instance_type = fields.Str()


class KubernetesOnlineDeploymentSchema(OnlineDeploymentSchema):
    resources = NestedField(ResourceRequirementsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import KubernetesOnlineDeployment

        return KubernetesOnlineDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class ManagedOnlineDeploymentSchema(OnlineDeploymentSchema):
    instance_type = fields.Str(required=True)
    egress_public_network_access = ExperimentalField(
        StringTransformedEnum(allowed_values=[PublicNetworkAccess.ENABLED, PublicNetworkAccess.DISABLED])
    )
    private_network_connection = ExperimentalField(fields.Bool())

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ManagedOnlineDeployment

        return ManagedOnlineDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
