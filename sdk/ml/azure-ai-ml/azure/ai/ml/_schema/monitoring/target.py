# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load


from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._monitoring import MonitorTargetTasks
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr, StringTransformedEnum


class MonitoringTargetSchema(metaclass=PatchedSchemaMeta):
    model_id = ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL)
    ml_task = StringTransformedEnum(allowed_values=[o.value for o in MonitorTargetTasks])
    endpoint_deployment_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.target import MonitoringTarget

        return MonitoringTarget(**data)
