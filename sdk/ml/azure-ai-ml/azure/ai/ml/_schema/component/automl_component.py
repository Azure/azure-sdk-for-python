# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._restclient.v2022_10_01_preview.models import TaskType
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import JobType


class AutoMLComponentSchema(ComponentSchema):
    """AutoMl component schema.

    Only has type & task property with basic component properties. No inputs & outputs are allowed.
    """

    type = StringTransformedEnum(required=True, allowed_values=JobType.AUTOML)
    task = StringTransformedEnum(
        # TODO: verify if this works
        allowed_values=[t for t in TaskType],  # pylint: disable=unnecessary-comprehension
        casing_transform=camel_to_snake,
        required=True,
    )
