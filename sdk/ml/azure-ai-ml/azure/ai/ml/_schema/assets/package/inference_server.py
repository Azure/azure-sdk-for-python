# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load, pre_load, ValidationError
from .online_inference_configuration import OnlineInferenceConfigurationSchema
from azure.ai.ml._schema._deployment.code_configuration_schema import CodeConfigurationSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.constants._common import InferenceServerType


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

    @pre_load
    def pre_load(self, data, **kwargs):
        if data["type"] == InferenceServerType.AZUREML_ONLINE or data["type"] == InferenceServerType.AZUREML_BATCH:
            if "code_configuration" not in data:
                raise ValidationError("code_configuration is required for online and batch inference servers")

        if data["type"] == InferenceServerType.CUSTOM or data["type"] == InferenceServerType.TRITON:
            if "inference_configuration" not in data:
                raise ValidationError("inference_configuration is required for custom and triton inference servers")
        return data

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
        return TritonInferencingServer(**data)
