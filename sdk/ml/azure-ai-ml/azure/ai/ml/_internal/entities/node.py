# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

from enum import Enum
from typing import Dict, List, Optional, Union

from marshmallow import Schema

from ... import Input, Output
from ..._schema import PathAwareSchema
from ...constants import JobType
from ...entities import Component, Job
from ...entities._builders import BaseNode
from ...entities._job.pipeline._io import NodeInput, NodeOutput, PipelineInput
from ...entities._util import convert_ordered_dict_to_dict
from .._schema.component import NodeType


class InternalBaseNode(BaseNode):
    """Base class for node of internal components in pipeline. Can be instantiated directly.

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
        type: str = JobType.COMPONENT,  # pylint: disable=redefined-builtin
        component: Union[Component, str],
        inputs: Optional[
            Dict[
                str,
                Union[
                    PipelineInput,
                    NodeOutput,
                    Input,
                    str,
                    bool,
                    int,
                    float,
                    Enum,
                    "Input",
                ],
            ]
        ] = None,
        outputs: Optional[Dict[str, Union[str, Output, "Output"]]] = None,
        properties: Optional[Dict] = None,
        compute: Optional[str] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)
        BaseNode.__init__(
            self,
            type=type,
            component=component,  # type: ignore[arg-type]
            # TODO: Bug 2881892
            inputs=inputs,
            outputs=outputs,
            compute=compute,
            properties=properties,
            **kwargs,
        )

    @property
    def _skip_required_compute_missing_validation(self) -> bool:
        return True

    def _to_node(self, context: Optional[Dict] = None, **kwargs) -> BaseNode:
        return self

    def _to_component(self, context: Optional[Dict] = None, **kwargs) -> Component:
        return self.component

    def _to_job(self) -> Job:
        raise RuntimeError("Internal components doesn't support to job")

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Job":
        raise RuntimeError("Internal components doesn't support load from dict")

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.node import InternalBaseNodeSchema

        return InternalBaseNodeSchema(context=context)

    @property
    def component(self) -> Component:
        return self._component

    def _to_rest_inputs(self) -> Dict[str, Dict]:
        rest_dataset_literal_inputs = super(InternalBaseNode, self)._to_rest_inputs()
        for input_name, input_value in self.inputs.items():
            # hack: remove unfilled input from rest object instead a default input of {"job_input_type": "literal"}
            # note that this hack is not always effective as _data will be set to Input() when visiting input_value.type
            if (
                isinstance(input_value, NodeInput)
                and input_value._data is None
                and input_name in rest_dataset_literal_inputs
            ):
                del rest_dataset_literal_inputs[input_name]
        return rest_dataset_literal_inputs

    def _to_rest_object(self, **kwargs) -> dict:
        base_dict = super(InternalBaseNode, self)._to_rest_object(**kwargs)
        for key in ["name", "display_name", "tags"]:
            if key in base_dict:
                del base_dict[key]
        for key in ["computeId"]:
            if key in base_dict and base_dict[key] is None:
                del base_dict[key]

        base_dict.update(
            convert_ordered_dict_to_dict(
                {
                    "componentId": self._get_component_id(),
                    "type": self.type,
                }
            )
        )
        return base_dict


class DataTransfer(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(DataTransfer, self).__init__(type=NodeType.DATA_TRANSFER, **kwargs)


class HDInsight(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(HDInsight, self).__init__(type=NodeType.HDI, **kwargs)
        self._init = True
        self._compute_name: str = kwargs.pop("compute_name", None)
        self._queue: str = kwargs.pop("queue", None)
        self._driver_memory: str = kwargs.pop("driver_memory", None)
        self._driver_cores: int = kwargs.pop("driver_cores", None)
        self._executor_memory: str = kwargs.pop("executor_memory", None)
        self._executor_cores: int = kwargs.pop("executor_cores", None)
        self._number_executors: int = kwargs.pop("number_executors", None)
        self._conf: Union[dict, str] = kwargs.pop("conf", None)
        self._hdinsight_spark_job_name: str = kwargs.pop("hdinsight_spark_job_name", None)
        self._init = False

    @property
    def compute_name(self) -> str:
        """Name of the compute to be used.

        :return: Compute name
        :rtype: str
        """
        return self._compute_name

    @compute_name.setter
    def compute_name(self, value: str):
        self._compute_name = value

    @property
    def queue(self) -> str:
        """The name of the YARN queue to which submitted.

        :return: YARN queue name
        :rtype: str
        """
        return self._queue

    @queue.setter
    def queue(self, value: str):
        self._queue = value

    @property
    def driver_memory(self) -> str:
        """Amount of memory to use for the driver process.

        It's the same format as JVM memory strings. Use lower-case suffixes, e.g. k, m, g, t, and p, for kilobyte,
        megabyte, gigabyte and terabyte respectively. Example values are 10k, 10m and 10g.

        :return: Amount of memory to use for the driver process
        :rtype: str
        """
        return self._driver_memory

    @driver_memory.setter
    def driver_memory(self, value: str):
        self._driver_memory = value

    @property
    def driver_cores(self) -> int:
        """Number of cores to use for the driver process.

        :return: Number of cores to use for the driver process.
        :rtype: int
        """
        return self._driver_cores

    @driver_cores.setter
    def driver_cores(self, value: int):
        self._driver_cores = value

    @property
    def executor_memory(self) -> str:
        """Amount of memory to use per executor process.

        It's the same format as JVM memory strings. Use lower-case suffixes, e.g. k, m, g, t, and p, for kilobyte,
        megabyte, gigabyte and terabyte respectively. Example values are 10k, 10m and 10g.

        :return: The executor memory
        :rtype: str
        """
        return self._executor_memory

    @executor_memory.setter
    def executor_memory(self, value: str):
        self._executor_memory = value

    @property
    def executor_cores(self) -> int:
        """Number of cores to use for each executor.

        :return: The number of cores to use for each executor
        :rtype: int
        """
        return self._executor_cores

    @executor_cores.setter
    def executor_cores(self, value: int):
        self._executor_cores = value

    @property
    def number_executors(self) -> int:
        """Number of executors to launch for this session.

        :return: The number of executors to launch
        :rtype: int
        """
        return self._number_executors

    @number_executors.setter
    def number_executors(self, value: int):
        self._number_executors = value

    @property
    def conf(self) -> Union[dict, str]:
        """Spark configuration properties.

        :return: The spark configuration properties.
        :rtype: Union[dict, str]
        """
        return self._conf

    @conf.setter
    def conf(self, value: Union[dict, str]):
        self._conf = value

    @property
    def hdinsight_spark_job_name(self) -> str:
        """

        :return: The name of this session
        :rtype: str
        """
        return self._hdinsight_spark_job_name

    @hdinsight_spark_job_name.setter
    def hdinsight_spark_job_name(self, value: str):
        self._hdinsight_spark_job_name = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return [
            "compute_name",
            "queue",
            "driver_cores",
            "executor_memory",
            "conf",
            "hdinsight_spark_job_name",
            "driver_memory",
            "executor_cores",
            "number_executors",
        ]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.node import HDInsightSchema

        return HDInsightSchema(context=context)


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


class AetherBridge(InternalBaseNode):
    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(AetherBridge, self).__init__(type=NodeType.AETHER_BRIDGE, **kwargs)
