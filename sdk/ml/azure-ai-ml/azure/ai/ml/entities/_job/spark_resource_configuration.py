# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    SparkResourceConfiguration as RestSparkResourceConfiguration,
)
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class SparkResourceConfiguration(RestTranslatableMixin, DictMixin):
    instance_type_list = [
        "standard_e4s_v3",
        "standard_e8s_v3",
        "standard_e16s_v3",
        "standard_e32s_v3",
        "standard_e64s_v3",
    ]

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
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.instance_type.lower() not in self.instance_type_list:
            msg = "Instance type must be specified for the list of {}".format(",".join(self.instance_type_list))
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

        # runtime_version type is either float or str
        if isinstance(self.runtime_version, float):
            if self.runtime_version < 3.1 or self.runtime_version >= 3.3:
                msg = "runtime version should be either 3.1 or 3.2"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SPARK_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
        elif isinstance(self.runtime_version, str):
            runtime_arr = self.runtime_version.split(".")
            try:
                for runtime in runtime_arr:
                    int(runtime)
            except ValueError:
                raise ValueError("runtime_version should only contain numbers")
            if len(runtime_arr) <= 1:
                msg = "runtime version should be either 3.1 or 3.2"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SPARK_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
            first_number = int(runtime_arr[0])
            second_number = int(runtime_arr[1])
            if first_number != 3 or second_number not in (1, 2):
                msg = "runtime version should be either 3.1 or 3.2"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SPARK_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            msg = "runtime version should be either float or str type"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
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
