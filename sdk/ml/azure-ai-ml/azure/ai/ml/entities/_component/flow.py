# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from marshmallow import EXCLUDE, Schema, ValidationError

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, COMPONENT_TYPE, SchemaUrl
from azure.ai.ml.constants._component import NodeType

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._schema.component.flow import FlowComponentSchema, FlowSchema, RunSchema
from ...exceptions import ErrorCategory, ValidationException
from ._additional_includes import AdditionalIncludesMixin
from .component import Component

# pylint: disable=protected-access


class FlowComponentPort(dict):
    def __iter__(self):
        raise RuntimeError("Ports of flow component are not readable before creation.")

    def keys(self):
        raise RuntimeError("Ports of flow component are not readable before creation.")

    def __setitem__(self, key, value):
        raise RuntimeError("Ports of flow component are not editable.")

    def __getitem__(self, item):
        raise RuntimeError("Ports of flow component are not readable before creation.")


class FlowComponent(Component, AdditionalIncludesMixin):
    """Command component version, used to define a Command Component or Job.

    :keyword name: The name of the Command job or component.
    :type name: Optional[str]
    :keyword version: The version of the Command job or component.
    :type version: Optional[str]
    :keyword description: The description of the component. Defaults to None.
    :type description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict]
    :keyword display_name: The display name of the component.
    :type display_name: Optional[str]
    :keyword command: The command to be executed.
    :type command: Optional[str]
    :keyword is_deterministic: Specifies whether the Command will return the same output given the same input.
        Defaults to True. When True, if a Command (component) is deterministic and has been run before in the
        current workspace with the same input and settings, it will reuse results from a previous submitted job
        when used as a node or step in a pipeline. In that scenario, no compute resources will be used.
    :type is_deterministic: Optional[bool]
    :keyword additional_includes: A list of shared additional files to be included in the component. Defaults to None.
    :type additional_includes: Optional[list[str]]
    :keyword properties: The job property dictionary. Defaults to None.
    :type properties: Optional[dict[str, str]]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if CommandComponent cannot be successfully validated.
        Details will be provided in the error message.

    .. admonition:: Example:


        .. literalinclude:: ../../../../../samples/ml_samples_command_configurations.py
            :start-after: [START command_component_definition]
            :end-before: [END command_component_definition]
            :language: python
            :dedent: 8
            :caption: Creating a CommandComponent.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        display_name: Optional[str] = None,
        is_deterministic: bool = True,
        additional_includes: Optional[List] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ) -> None:
        # validate init params are valid type
        kwargs[COMPONENT_TYPE] = NodeType.FLOW_PARALLEL

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs={},
            outputs={},
            is_deterministic=is_deterministic,
            properties=properties,
            **kwargs,
        )

        self._inputs, self._outputs = FlowComponentPort(), FlowComponentPort()

        self.additional_includes = additional_includes or []

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        raise RuntimeError("FlowComponent does not support loading from REST object.")

    # region SchemaValidatableMixin
    @classmethod
    def _load_with_schema(cls, data, *, context=None, raise_original_exception=False, **kwargs):
        # FlowComponent should be loaded with FlowSchema or FlowRunSchema instead of FlowComponentSchema
        context = context or {BASE_PATH_CONTEXT_KEY: Path.cwd()}
        _schema = data.get("$schema", None)
        if _schema == SchemaUrl.PROMPTFLOW_RUN:
            schema = RunSchema(context=context)
        elif _schema == SchemaUrl.PROMPTFLOW_FLOW:
            schema = FlowSchema(context=context)
        else:
            raise ValidationException(
                message="$schema must be specified correctly for loading component from flow, but got %s" % _schema,
                no_personal_data_message="$schema must be specified for loading component from flow",
                target=cls._get_validation_error_target(),
                error_category=ErrorCategory.USER_ERROR,
            )

        # unlike other component, we should ignore unknown fields in flow to keep init_params clean and avoid
        # too much understanding of flow.dag.yaml & run.yaml
        kwargs["unknown"] = EXCLUDE
        try:
            return schema.load(data, **kwargs)
        except ValidationError as e:
            if raise_original_exception:
                raise e
            msg = "Trying to load data with schema failed. Data:\n%s\nError: %s" % (
                json.dumps(data, indent=4) if isinstance(data, dict) else data,
                json.dumps(e.messages, indent=4),
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=str(e),
                target=cls._get_validation_error_target(),
                error_category=ErrorCategory.USER_ERROR,
            ) from e

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return FlowComponentSchema(context=context)

    # endregion
