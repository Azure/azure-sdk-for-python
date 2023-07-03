# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Union

from azure.ai.ml import Input, Output
from azure.ai.ml._schema.component.input_output import SUPPORTED_PARAM_TYPES
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.entities._inputs_outputs.utils import _remove_empty_values
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin


class _InputOutputBase(DictMixin, RestTranslatableMixin):
    def __init__(
        self,
        *,
        type,  # pylint: disable=redefined-builtin
        **kwargs,  # pylint: disable=unused-argument
    ):
        """Base class for Input & Output class.

        This class is introduced to support literal output in the future.

        :param type: The type of the Input/Output.
        :type type: str
        """
        self.type = type

    def _is_literal(self) -> bool:
        """Returns True if this input is literal input."""
        return self.type in SUPPORTED_PARAM_TYPES

    @property
    def _is_control_or_primitive_type(self):
        return getattr(self, "is_control", None) or getattr(self, "_is_primitive_type", None)


class Meta(object):
    """This is the meta data of Inputs/Outputs."""

    def __init__(
        self,
        type=None,
        description=None,
        min=None,
        max=None,
        **kwargs,
    ):
        self.type = type
        self.description = description
        self._min = min
        self._max = max
        self._default = kwargs.pop("default", None)
        self._kwargs = kwargs

    def _to_io_entity_args_dict(self):
        """Convert the object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = set(Output._IO_KEYS + Input._IO_KEYS)  # pylint: disable=protected-access
        result = {key: getattr(self, key, None) for key in keys}
        result.update(self._kwargs)
        if IOConstants.PRIMITIVE_TYPE_2_STR.get(self.type) is not None:
            result["type"] = IOConstants.PRIMITIVE_TYPE_2_STR.get(self.type)
        return _remove_empty_values(result)

    @property
    def max(self) -> Optional[Union[int, float]]:
        """Return the maximum value of the parameter for a numeric parameter."""
        return self._max

    @property
    def min(self) -> Optional[Union[int, float]]:
        """Return the minimum value of the parameter for a numeric parameter."""
        return self._min

    @property
    def default(self):
        """Return the default value of the parameter."""
        return self._default
