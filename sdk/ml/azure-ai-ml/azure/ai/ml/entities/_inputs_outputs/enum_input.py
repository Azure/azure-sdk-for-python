# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import EnumMeta
from typing import Any, Iterable, List, Optional, Sequence, Tuple, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .input import Input


class EnumInput(Input):
    """Enum parameter parse the value according to its enum values."""

    def __init__(
        self,
        *,
        enum: Optional[Union[EnumMeta, Sequence[str]]] = None,
        default: Any = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Enum parameter parse the value according to its enum values.

        :param enum: Enum values.
        :type enum: Union[EnumMeta, Sequence[str]]
        :param default: Default value of the parameter
        :type default: Any
        :param description: Description of the parameter
        :type description: str
        """
        enum_values = self._assert_enum_valid(enum)
        self._enum_class: Optional[EnumMeta] = None
        # This is used to parse enum class instead of enum str value if a enum class is provided.
        if isinstance(enum, EnumMeta):
            self._enum_class = enum
            self._str2enum = dict(zip(enum_values, enum))
        else:
            self._str2enum = {v: v for v in enum_values}
        super().__init__(type="string", default=default, enum=enum_values, description=description)

    @property
    def _allowed_types(self) -> Tuple:
        return (
            (str,)
            if not self._enum_class
            else (
                self._enum_class,
                str,
            )
        )

    @classmethod
    def _assert_enum_valid(cls, enum: Optional[Union[EnumMeta, Sequence[str]]]) -> List:
        """Check whether the enum is valid and return the values of the enum.

        :param enum: The enum to validate
        :type enum: Type
        :return: The enum values
        :rtype: List[Any]
        """
        if isinstance(enum, EnumMeta):
            enum_values = [str(option.value) for option in enum]  # type: ignore
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

    def _parse(self, val: str) -> Any:
        """Parse the enum value from a string value or the enum value.

        :param val: The string to parse
        :type val: str
        :return: The enum value
        :rtype: Any
        """
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

    def _update_default(self, default_value: Any) -> None:
        """Enum parameter support updating values with a string value.

        :param default_value: The default value for the input
        :type default_value: Any
        """
        enum_val = self._parse(default_value)
        if self._enum_class and isinstance(enum_val, self._enum_class):
            enum_val = enum_val.value
        self.default = enum_val
