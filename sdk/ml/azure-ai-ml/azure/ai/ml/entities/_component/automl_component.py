# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import typing

from marshmallow import Schema

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.component.automl_component import AutoMLComponentSchema
from azure.ai.ml.constants import COMPONENT_TYPE, NodeType
from azure.ai.ml.entities._component.component import Component


class AutoMLComponent(Component):
    """AutoML component entity, used to define an automl component.

    AutoML Component will only be used "internally" for the mentioned
    scenarios that need it. AutoML Component schema is not intended to
    be used by the end users and therefore it won't be provided to the
    end users and it won't have public documentation for the users.
    """

    def __init__(
        self,
        *,
        task: str = None,
        **kwargs,
    ):
        """Initialize an AutoML component entity.

        :param task: Task of the component.
        :type task: str
        :param kwargs:
        """
        kwargs[COMPONENT_TYPE] = NodeType.AUTOML
        super(AutoMLComponent, self).__init__(**kwargs)
        self._task = task

    @property
    def task(self):
        """Returns task of the component."""
        return self._task

    @classmethod
    def _create_schema_for_validation(cls, context) -> typing.Union[PathAwareSchema, Schema]:
        return AutoMLComponentSchema(context=context)
