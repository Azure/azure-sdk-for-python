# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,redefined-builtin,no-else-return

import logging

from marshmallow import post_load
from azure.ai.ml._schema._deployment.code_configuration_schema import CodeConfigurationSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.constants._common import InferenceServerType
from .online_inference_configuration import OnlineInferenceConfigurationSchema


module_logger = logging.getLogger(__name__)


class InferenceServerSchema(PathAwareSchema):
    type = StringTransformedEnum(
        allowed_values=[
            InferenceServerType.AZUREML_ONLINE,
            InferenceServerType.AZUREML_BATCH,
            InferenceServerType.CUSTOM,
            InferenceServerType.TRITON,
        ],
        required=True,
    )
    code_configuration = NestedField(CodeConfigurationSchema)  # required for batch and online
    inference_configuration = NestedField(OnlineInferenceConfigurationSchema)  # required for custom and Triton

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import (
            AzureMLOnlineInferencingServer,
            AzureMLBatchInferencingServer,
            CustomInferencingServer,
            TritonInferencingServer,
        )

        if data["type"] == InferenceServerType.AZUREML_ONLINE:
            return AzureMLOnlineInferencingServer(**data)
        elif data["type"] == InferenceServerType.AZUREML_BATCH:
            return AzureMLBatchInferencingServer(**data)
        elif data["type"] == InferenceServerType.CUSTOM:
            return CustomInferencingServer(**data)
        elif data["type"] == InferenceServerType.TRITON:
            return TritonInferencingServer(**data)
        else:
            return None
