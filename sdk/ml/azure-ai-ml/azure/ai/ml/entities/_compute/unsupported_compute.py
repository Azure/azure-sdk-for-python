# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict

from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource
from azure.ai.ml.constants._common import TYPE
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class UnsupportedCompute(Compute):
    """Unsupported compute resource.

    Only used for displaying compute properties for resources not fully supported in the SDK.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = "*** Unsupported Compute Type ***"
        super().__init__(**kwargs)

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "UnsupportedCompute":
        prop = rest_obj.properties
        if hasattr(rest_obj, "tags"):
            # TODO(2294131): remove this when DataFactory object has no tags got fixed
            tags = rest_obj.tags
        else:
            tags = None
        response = UnsupportedCompute(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            tags=tags,
            provisioning_state=prop.provisioning_state,
            created_on=prop.additional_properties.get("createdOn", None),
        )
        return response

    @classmethod
    # pylint: disable=unused-argument
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "UnsupportedCompute":
        msg = "Cannot create unsupported compute type."
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )

    def _to_rest_object(self) -> ComputeResource:
        msg = "Cannot create unsupported compute type."
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )
