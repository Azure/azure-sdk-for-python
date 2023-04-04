# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr
from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitorInputDataSchema():
    input_dataset = ArmVersionedStr(azureml_type=AzureMLResourceType.DATA)
    dataset_context = fields.Str()
    target_column_name = fields.Str()
    pre_processing_component = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_input_data import MonitorInputData

        return MonitorInputData(**data)
