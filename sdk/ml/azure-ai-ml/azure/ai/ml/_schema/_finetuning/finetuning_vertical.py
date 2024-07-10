# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._schema._finetuning.finetuning_job import FineTuningJobSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml.constants import JobType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema, DataInputSchema, ModelInputSchema
from azure.ai.ml._restclient.v2024_01_01_preview.models import FineTuningTaskType
from azure.ai.ml.constants._job.finetuning import FineTuningConstants
from azure.ai.ml._utils._experimental import experimental

# This is meant to match the yaml definition NOT the models defined in _restclient


@experimental
class FineTuningVerticalSchema(FineTuningJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.FINE_TUNING)
    model = NestedField(ModelInputSchema, required=True)
    training_data = UnionField([NestedField(MLTableInputSchema), NestedField(DataInputSchema)])
    validation_data = UnionField([NestedField(MLTableInputSchema), NestedField(DataInputSchema)])
    task = StringTransformedEnum(
        allowed_values=[
            FineTuningTaskType.CHAT_COMPLETION,
            FineTuningTaskType.TEXT_COMPLETION,
            FineTuningTaskType.TEXT_CLASSIFICATION,
            FineTuningTaskType.QUESTION_ANSWERING,
            FineTuningTaskType.TEXT_SUMMARIZATION,
            FineTuningTaskType.TOKEN_CLASSIFICATION,
            FineTuningTaskType.TEXT_TRANSLATION,
            FineTuningTaskType.IMAGE_CLASSIFICATION,
            FineTuningTaskType.IMAGE_INSTANCE_SEGMENTATION,
            FineTuningTaskType.IMAGE_OBJECT_DETECTION,
            FineTuningTaskType.VIDEO_MULTI_OBJECT_TRACKING,
        ],
        casing_transform=camel_to_snake,
        data_key=FineTuningConstants.TaskType,
        required=True,
    )
