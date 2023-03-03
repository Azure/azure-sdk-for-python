# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load
from .online_inference_configuration import OnlineInferenceConfigurationSchema
from azure.ai.ml._schema._deployment.code_configuration_schema import CodeConfigurationSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._common import InferenceServerType

module_logger = logging.getLogger(__name__)


class InferenceServerSchema(PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            InferenceServerType.AZUREML_ONLINE,
            InferenceServerType.AZUREML_BATCH,
            InferenceServerType.CUSTOM,
            InferenceServerType.TRITON,
        ]
    )
    code_configuration = NestedField(CodeConfigurationSchema)
    inference_configuration = NestedField(OnlineInferenceConfigurationSchema)
