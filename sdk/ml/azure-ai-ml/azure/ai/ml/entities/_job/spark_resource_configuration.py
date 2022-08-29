# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2022_06_01_preview.models import (
    SparkResourceConfiguration as RestSparkResourceConfiguration,
)
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException


class SparkResourceConfiguration(RestTranslatableMixin, DictMixin):
    def __init__(self, *, instance_type: str = None, runtime_version: str = None):
        self.instance_type = instance_type
        self.runtime_version = runtime_version

    def _to_rest_object(self) -> RestSparkResourceConfiguration:
        return RestSparkResourceConfiguration(instance_type=self.instance_type, runtime_version=self.runtime_version)

    @classmethod
    def _from_rest_object(cls, obj: Optional[RestSparkResourceConfiguration]) -> Optional["SparkResourceConfiguration"]:
        if obj is None:
            return None
        return SparkResourceConfiguration(instance_type=obj.instance_type, runtime_version=obj.runtime_version)

    def _validate(self):
        if self.instance_type is None or self.instance_type == "":
            msg = "Instance type must be specified for SparkResourceConfiguration"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SparkResourceConfiguration):
            return NotImplemented
        return self.instance_type == other.instance_type and self.runtime_version == other.runtime_version

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SparkResourceConfiguration):
            return NotImplemented
        return not self.__eq__(other)

    def _merge_with(self, other: "SparkResourceConfiguration") -> None:
        if other:
            if other.instance_type:
                self.instance_type = other.instance_type
            if other.runtime_version:
                self.runtime_version = other.runtime_version
