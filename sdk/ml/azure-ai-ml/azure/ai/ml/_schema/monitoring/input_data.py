# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._monitoring import MonitorDatasetContext
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr, StringTransformedEnum


class MonitorInputDataSchema(metaclass=PatchedSchemaMeta):
    input_dataset = ArmVersionedStr(azureml_type=AzureMLResourceType.DATA)
    dataset_context = StringTransformedEnum(allowed_values=[o.value for o in MonitorDatasetContext])
    target_column_name = fields.Str()
    pre_processing_component = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.input_data import MonitorInputData

        return MonitorInputData(**data)
