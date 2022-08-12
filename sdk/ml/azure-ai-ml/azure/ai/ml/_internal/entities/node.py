# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from enum import Enum
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml import Input, Output
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities import Component, Job, ResourceConfiguration
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutputBase
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict

from .._schema.component import NodeType
from ...entities._validation import ValidationResult


class InternalBaseNode(BaseNode):
    """Base class for node of internal components in pipeline. Can be
    instantiated directly.

    :param type: Type of pipeline node
    :type type: str
    :param component: Id or instance of the component version to be run for the step
    :type component: Union[Component, str]
    :param inputs: Inputs to the node.
    :type inputs: Dict[str, Union[Input, str, bool, int, float, Enum, dict]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    :param compute: Compute definition containing the compute information for the step
    :type compute: str
    """

    def __init__(
        self,
        *,
        type: str = JobType.COMPONENT,
        component: Union[Component, str],
        inputs: Dict[
            str,
            Union[
                PipelineInput,
                PipelineOutputBase,
                Input,
                str,
                bool,
                int,
                float,
                Enum,
                "Input",
            ],
        ] = None,
        outputs: Dict[str, Union[str, Output, "Output"]] = None,
        properties: Dict = None,
        compute: str = None,
        **kwargs,
    ):
        kwargs.pop("type", None)
        BaseNode.__init__(
            self,
            type=type,
            component=component,
            inputs=inputs,
            outputs=outputs,
            compute=compute,
            properties=properties,
            **kwargs,
        )

    @property
    def _skip_required_compute_missing_validation(self) -> bool:
        return True

    def _to_node(self, **kwargs) -> BaseNode:
        return self

    def _to_component(self, **kwargs) -> Component:
        return self.component

    def _to_job(self) -> Job:
        raise RuntimeError("Internal components doesn't support to job")

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Job":
        raise RuntimeError("Internal components doesn't support load from dict")

    def _schema_validate(self) -> ValidationResult:
        """Validate the resource with the schema.

        return type: ValidationResult
        """
        result = super(InternalBaseNode, self)._schema_validate()
        # skip unknown field warnings for internal components
        # TODO: move this logic into base class?
        result._warnings = list(filter(lambda x: x.descriptor.message != "Unknown field.", result._warnings))
        return result

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.node import InternalBaseNodeSchema

        return InternalBaseNodeSchema(context=context)

    @property
    def component(self) -> Component:
        return self._component

    def _to_rest_object(self, **kwargs) -> dict:
        base_dict = super(InternalBaseNode, self)._to_rest_object(**kwargs)
        for key in ["name", "display_name", "tags"]:
            if key in base_dict:
                del base_dict[key]

        if "computeId" in base_dict and base_dict["computeId"] is None:
            del base_dict["computeId"]

        base_dict.update(
            convert_ordered_dict_to_dict(
                dict(
                    componentId=self._get_component_id(),
                    type=self.type,
                )
            )
        )
        return base_dict

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "InternalBaseNode":
        obj = cls._rest_object_to_init_params(obj)

        # Change componentId -> component
        component_id = obj.pop("componentId", None)
        obj["component"] = component_id

        instance = cls.__new__(cls)
        instance.__init__(**obj)
        return instance


class DataTransfer(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(DataTransfer, self).__init__(type=NodeType.DATA_TRANSFER, **kwargs)


class HDInsight(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(HDInsight, self).__init__(type=NodeType.HDI, **kwargs)


class Parallel(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Parallel, self).__init__(type=NodeType.PARALLEL, **kwargs)


class Starlite(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Starlite, self).__init__(type=NodeType.STARLITE, **kwargs)


class Pipeline(InternalBaseNode):
    # this is only for using registered pipeline component
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Pipeline, self).__init__(type=NodeType.PIPELINE, **kwargs)


class Hemera(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Hemera, self).__init__(type=NodeType.HEMERA, **kwargs)


class Ae365exepool(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Ae365exepool, self).__init__(type=NodeType.AE365EXEPOOL, **kwargs)


class Sweep(InternalBaseNode):
    # this is not in our scope
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Sweep, self).__init__(type=NodeType.SWEEP, **kwargs)
