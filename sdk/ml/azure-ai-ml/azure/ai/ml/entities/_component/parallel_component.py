# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import re
import os
from marshmallow import INCLUDE, Schema
from typing import Dict, Any, Union

from azure.ai.ml._restclient.v2021_10_01.models import (
    ComponentVersionData,
    ComponentVersionDetails,
)
from azure.ai.ml._schema.component.parallel_component import ParallelComponentSchema, RestParallelComponentSchema
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    COMPONENT_TYPE,
    NodeType,
    ComponentSource,
)
from azure.ai.ml.entities._component.input_output import ComponentInput, ComponentOutput
from .component import Component
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._job.parallel.retry_settings import RetrySettings
from azure.ai.ml.entities._job.parallel.parameterized_parallel import ParameterizedParallel
from azure.ai.ml.entities._job.parallel.parallel_task import ParallelTask
from .._util import validate_attribute_type

from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from ..._schema import PathAwareSchema


class ParallelComponent(Component, ParameterizedParallel):
    """Parallel component version, used to define a parallel component.

    :param name: Name of the component.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param description: Description of the component.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param retry_settings: parallel component run failed retry
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has.
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored.
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored.
    :type mini_batch_error_threshold: int
    :param task: The parallel task.
    :type task: ParallelTask
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.) This value could be set
        through PipelineParameter.
    :type mini_batch_size: str
    :param input_data: The input data.
    :type input_data: str
    :param resources: Compute Resource configuration for the component.
    :type resources: Union[dict, ~azure.ai.ml.entities.ResourceConfiguration]
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param code: promoted property from task.code
    :type code: str
    :param instance_count: promoted property from resources.instance_count
    :type instance_count: int
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        display_name: str = None,
        retry_settings: RetrySettings = None,
        logging_level: str = None,
        max_concurrency_per_instance: int = None,
        error_threshold: int = None,
        mini_batch_error_threshold: int = None,
        task: ParallelTask = None,
        mini_batch_size: str = None,
        input_data: str = None,
        resources: ResourceConfiguration = None,
        inputs: Dict = None,
        outputs: Dict = None,
        code: str = None,  # promoted property from task.code
        instance_count: int = None,  # promoted property from resources.instance_count
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.PARALLEL

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

        # No validation on value passed here because in pipeline job, required code&environment maybe absent
        # and fill in later with job defaults.
        self.task = task
        self.mini_batch_size = mini_batch_size
        self.input_data = input_data
        self.retry_settings = retry_settings
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.error_threshold = error_threshold
        self.mini_batch_error_threshold = mini_batch_error_threshold
        self.resources = resources

        # check mutual exclusivity of promoted properties
        if self.resources is not None and instance_count is not None:
            msg = "instance_count and resources are mutually exclusive"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        self.instance_count = instance_count
        self.code = code

        if self.mini_batch_size is not None:
            """Convert str to int."""
            pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
            if not pattern.match(self.mini_batch_size):
                raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$")

            try:
                self.mini_batch_size = int(self.mini_batch_size)
            except ValueError:
                unit = self.mini_batch_size[-2:].lower()
                if unit == "kb":
                    self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024
                elif unit == "mb":
                    self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024
                elif unit == "gb":
                    self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024 * 1024
                else:
                    raise ValueError("mini_batch_size unit must be kb, mb or gb")

    @property
    def instance_count(self) -> int:
        """
        Return value of promoted property resources.instance_count.

        :return: Value of resources.instance_count.
        :rtype: Optional[int]
        """
        return self.resources.instance_count if self.resources else None

    @instance_count.setter
    def instance_count(self, value: int):
        if not value:
            return
        if not self.resources:
            self.resources = ResourceConfiguration(instance_count=value)
        else:
            self.resources.instance_count = value

    @property
    def code(self) -> str:
        """
        Return value of promoted property task.code,
        which is a local or remote path pointing at source code.

        :return: Value of task.code.
        :rtype: Optional[str]
        """
        return self.task.code if self.task else None

    @code.setter
    def code(self, value: str):
        if not value:
            return
        if not self.task:
            self.task = ParallelTask(code=value)
        else:
            self.task.code = value

    @property
    def environment(self) -> str:
        """
        Return value of promoted property task.environment,
        indicate the environment that training job will run in.

        :return: Value of task.environment.
        :rtype: Optional[Environment, str]
        """
        return self.task.environment if self.task else None

    @environment.setter
    def environment(self, value: str):
        if not value:
            return
        if not self.task:
            self.task = ParallelTask(environment=value)
        else:
            self.task.environment = value

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "retry_settings": (dict, RetrySettings),
            "task": (dict, ParallelTask),
            "logging_level": str,
            "max_concurrency_per_instance": int,
            "input_data": str,
            "error_threshold": int,
            "mini_batch_error_threshold": int,
            "code": (str, os.PathLike),
            "resources": (dict, ResourceConfiguration),
        }

    def _to_dict(self) -> Dict:
        """Dump the parallel component content into a dictionary."""

        # Replace the name of $schema to schema.
        component_schema_dict = ParallelComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        component_schema_dict.pop("base_path", None)
        return {**self._other_parameter, **component_schema_dict}

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "ParallelComponent":
        return ParallelComponent(
            yaml_str=kwargs.pop("yaml_str", None),
            _source=kwargs.pop("_source", ComponentSource.YAML),
            **(ParallelComponentSchema(context=context).load(data, unknown=INCLUDE, **kwargs)),
        )

    def _to_rest_object(self) -> ComponentVersionData:
        self._validate(raise_error=True)
        # Convert nested ordered dict to dict.
        # TODO: we may need to use original dict from component YAML(only change code and environment), returning
        # parsed dict might add default value for some field, eg: if we add property "optional" with default value
        # to ComponentInput, it will add field "optional" to all inputs even if user doesn't specify one
        component = json.loads(json.dumps(self._to_dict()))

        properties = ComponentVersionDetails(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersionData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_rest(cls, obj: ComponentVersionData) -> "ParallelComponent":
        rest_component_version = obj.properties
        inputs = {
            k: ComponentInput._from_rest_object(v)
            for k, v in rest_component_version.component_spec.pop("inputs", {}).items()
        }
        outputs = {
            k: ComponentOutput._from_rest_object(v)
            for k, v in rest_component_version.component_spec.pop("outputs", {}).items()
        }
        parallel_component = ParallelComponent(
            id=obj.id,
            is_anonymous=rest_component_version.is_anonymous,
            creation_context=obj.system_data,
            inputs=inputs,
            outputs=outputs,
            **RestParallelComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).load(
                rest_component_version.component_spec, unknown=INCLUDE
            ),
            _source=ComponentSource.REST,
        )
        return parallel_component

    @classmethod
    def _get_schema(cls) -> Union[Schema, PathAwareSchema]:
        from azure.ai.ml._schema.component import ParallelComponentSchema

        return ParallelComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"})

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:
            return super(ParallelComponent, self).__str__()
