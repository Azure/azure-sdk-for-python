# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields

from azure.ai.ml._schema._finetuning.finetuning_job import FineTuningJobSchema
from azure.ai.ml._schema._finetuning.constants import SnakeCaseFineTuningTaskTypes
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    LocalPathField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml.constants import JobType
from azure.ai.ml._utils.utils import snake_to_camel
from azure.ai.ml._schema.job.input_output_entry import DataInputSchema, ModelInputSchema
from azure.ai.ml.constants._job.finetuning import FineTuningConstants
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import AzureMLResourceType


# This is meant to match the yaml definition NOT the models defined in _restclient


@experimental
class FineTuningVerticalSchema(FineTuningJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.FINE_TUNING)
    model = NestedField(ModelInputSchema, required=True)
    training_data = UnionField(
        [
            NestedField(DataInputSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATA),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(
                pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",
            ),
        ]
    )
    validation_data = UnionField(
        [
            NestedField(DataInputSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATA),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(
                pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",
            ),
        ]
    )

    task = StringTransformedEnum(
        allowed_values=[
            SnakeCaseFineTuningTaskTypes.CHAT_COMPLETION,
            SnakeCaseFineTuningTaskTypes.TEXT_COMPLETION,
            SnakeCaseFineTuningTaskTypes.TEXT_CLASSIFICATION,
            SnakeCaseFineTuningTaskTypes.QUESTION_ANSWERING,
            SnakeCaseFineTuningTaskTypes.TEXT_SUMMARIZATION,
            SnakeCaseFineTuningTaskTypes.TOKEN_CLASSIFICATION,
            SnakeCaseFineTuningTaskTypes.TEXT_TRANSLATION,
            SnakeCaseFineTuningTaskTypes.IMAGE_CLASSIFICATION,
            SnakeCaseFineTuningTaskTypes.IMAGE_INSTANCE_SEGMENTATION,
            SnakeCaseFineTuningTaskTypes.IMAGE_OBJECT_DETECTION,
            SnakeCaseFineTuningTaskTypes.VIDEO_MULTI_OBJECT_TRACKING,
        ],
        casing_transform=snake_to_camel,
        data_key=FineTuningConstants.TaskType,
        required=True,
    )
