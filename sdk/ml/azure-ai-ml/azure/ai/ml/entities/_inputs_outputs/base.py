# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._schema.component.input_output import SUPPORTED_PARAM_TYPES
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin


class _InputOutputBase(DictMixin, RestTranslatableMixin):
    def __init__(
        self,
        *,
        type,  # pylint: disable=redefined-builtin
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Base class for Input & Output class.

        This class is introduced to support literal output in the future.

        :param type: The type of the Input/Output.
        :type type: str
        """
        self.type = type

    def _is_literal(self) -> bool:
        """Check whether input is a literal

        :return: True if this input is literal input.
        :rtype: bool
        """
        return self.type in SUPPORTED_PARAM_TYPES
