# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.entities._job.automl.image.image_classification_search_space import ImageClassificationSearchSpace
from azure.ai.ml.entities._job.automl.image.image_object_detection_search_space import ImageObjectDetectionSearchSpace
from azure.ai.ml.entities._job.automl.search_space import SearchSpace


def cast_to_specific_search_space(
    input: Union[Dict, SearchSpace],
    class_name: Union[ImageClassificationSearchSpace, ImageObjectDetectionSearchSpace],
    task_type: str,
) -> Union[ImageClassificationSearchSpace, ImageObjectDetectionSearchSpace]:
    def validate_searchspace_args(input_dict: dict):
        searchspace = class_name()
        for key in input_dict:
            if not hasattr(searchspace, key):
                msg = f"Received unsupported search space parameter for {task_type} Job."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )

    if isinstance(input, dict):
        validate_searchspace_args(input)
        specific_search_space = class_name(**input)
    else:
        validate_searchspace_args(input.__dict__)
        specific_search_space = class_name._from_search_space_object(input)

    return specific_search_space
