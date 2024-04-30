# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TYPE_CHECKING, Dict, Type, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

if TYPE_CHECKING:
    from azure.ai.ml.entities._job.automl.image.image_classification_search_space import ImageClassificationSearchSpace
    from azure.ai.ml.entities._job.automl.image.image_object_detection_search_space import (
        ImageObjectDetectionSearchSpace,
    )
    from azure.ai.ml.entities._job.automl.nlp.nlp_search_space import NlpSearchSpace
    from azure.ai.ml.entities._job.automl.search_space import SearchSpace


def cast_to_specific_search_space(
    input: Union[Dict, "SearchSpace"],  # pylint: disable=redefined-builtin
    class_name: Union[
        Type["ImageClassificationSearchSpace"], Type["ImageObjectDetectionSearchSpace"], Type["NlpSearchSpace"]
    ],
    task_type: str,
) -> Union["ImageClassificationSearchSpace", "ImageObjectDetectionSearchSpace", "NlpSearchSpace"]:
    def validate_searchspace_args(input_dict: dict) -> None:
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
        specific_search_space = class_name._from_search_space_object(input)  # pylint: disable=protected-access

    res: Union["ImageClassificationSearchSpace", "ImageObjectDetectionSearchSpace", "NlpSearchSpace"] = (
        specific_search_space
    )
    return res
