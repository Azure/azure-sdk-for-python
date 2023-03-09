# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import EnumMeta
from typing import Iterable, Optional, Sequence, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .input import Input


class EnumInput(Input):
    """Enum parameter parse the value according to its enum values."""

    def __init__(
        self,
        *,
        enum: Optional[Union[EnumMeta, Sequence[str]]] = None,
        default=None,
        description=None,
        **kwargs,
    ):
        """Initialize an enum parameter, the options of an enum parameter are the enum values.

        :param enum: Enum values.
        :type Union[EnumMeta, Sequence[str]]
        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        enum_values = self._assert_enum_valid(enum)
        # This is used to parse enum class instead of enum str value if a enum class is provided.
        if isinstance(enum, EnumMeta):
            self._enum_class = enum
            self._str2enum = dict(zip(enum_values, enum))
        else:
            self._enum_class = None
            self._str2enum = {v: v for v in enum_values}
        super().__init__(type="string", default=default, enum=enum_values, description=description)

    @property
    def _allowed_types(self):
        return (
            (str,)
            if not self._enum_class
            else (
                self._enum_class,
                str,
            )
        )

    @classmethod
    def _assert_enum_valid(cls, enum):
        """Check whether the enum is valid and return the values of the enum."""
        if isinstance(enum, EnumMeta):
            enum_values = [str(option.value) for option in enum]
        elif isinstance(enum, Iterable):
            enum_values = list(enum)
        else:
            msg = "enum must be a subclass of Enum or an iterable."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if len(enum_values) <= 0:
            msg = "enum must have enum values."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if any(not isinstance(v, str) for v in enum_values):
            msg = "enum values must be str type."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        return enum_values

    def _parse(self, val: str):
        """Parse the enum value from a string value or the enum value."""
        if val is None:
            return val

        if self._enum_class and isinstance(val, self._enum_class):
            return val  # Directly return the enum value if it is the enum.

        if val not in self._str2enum:
            msg = "Not a valid enum value: '{}', valid values: {}"
            raise ValidationException(
                message=msg.format(val, ", ".join(self.enum)),
                no_personal_data_message=msg.format("[val]", "[enum]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return self._str2enum[val]

    def _update_default(self, default_value):
        """Enum parameter support updating values with a string value."""
        enum_val = self._parse(default_value)
        if self._enum_class and isinstance(enum_val, self._enum_class):
            enum_val = enum_val.value
        self.default = enum_val
