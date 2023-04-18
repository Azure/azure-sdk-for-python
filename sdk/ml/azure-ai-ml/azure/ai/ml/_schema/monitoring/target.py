# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load


from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr


class MonitoringTargetSchema(metaclass=PatchedSchemaMeta):
    endpoint_deployment_id = fields.Str()
    model_id = ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.target import MonitoringTarget

        return MonitoringTarget(**data)
