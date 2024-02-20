# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from azure.ai.ml._schema import ModelSchema
from azure.ai.ml.constants._common import AssetTypes

from ..core.fields import StringTransformedEnum

module_logger = logging.getLogger(__name__)


class MlflowModelSchema(ModelSchema):
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.MLFLOW_MODEL,
        ],
        metadata={"description": "The storage format for this entity. Used for NCD."},
    )