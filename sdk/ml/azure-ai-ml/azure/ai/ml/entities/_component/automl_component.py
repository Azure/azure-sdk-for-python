# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.component.automl_component import AutoMLComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._component.component import Component


class AutoMLComponent(Component):
    """AutoML component entity, used to define an automl component.

    AutoML Component will only be used "internally" for the mentioned scenarios that need it. AutoML Component schema is
    not intended to be used by the end users and therefore it won't be provided to the end users and it won't have
    public documentation for the users.

    :param task: Task of the component.
    :type task: str
    """

    def __init__(
        self,
        *,
        task: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[COMPONENT_TYPE] = NodeType.AUTOML
        super(AutoMLComponent, self).__init__(**kwargs)
        self._task = task

    @property
    def task(self) -> Optional[str]:
        """Returns task of the component."""
        return self._task

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> PathAwareSchema:
        return AutoMLComponentSchema(context=context)
