# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-instance-attributes

import copy
import logging
import re
from enum import Enum
from os import PathLike, path
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from marshmallow import INCLUDE, Schema

from ..._restclient.v2023_04_01_preview.models import JobBase as JobBaseData
from ..._restclient.v2023_04_01_preview.models import SparkJob as RestSparkJob
from ..._schema import NestedField, PathAwareSchema, UnionField
from ..._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from ..._schema.job.parameterized_spark import CONF_KEY_MAP
from ..._schema.job.spark_job import SparkJobSchema
from ..._utils.utils import is_url
from ...constants._common import (
    ARM_ID_PREFIX,
    BASE_PATH_CONTEXT_KEY,
    REGISTRY_URI_FORMAT,
    SPARK_ENVIRONMENT_WARNING_MESSAGE,
)
from ...constants._component import NodeType
from ...constants._job.job import SparkConfKey
from ...entities._assets import Environment
from ...entities._component.component import Component
from ...entities._component.spark_component import SparkComponent
from ...entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from ...entities._inputs_outputs import Input, Output
from ...entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    validate_inputs_for_args,
)
from ...entities._job.spark_job import SparkJob
from ...entities._job.spark_job_entry import SparkJobEntryType
from ...entities._job.spark_resource_configuration import SparkResourceConfiguration
from ...entities._validation import MutableValidationResult
from ...exceptions import ErrorCategory, ErrorTarget, ValidationException
from .._job.pipeline._io import NodeOutput
from .._job.spark_helpers import (
    _validate_compute_or_resources,
    _validate_input_output_mode,
    _validate_spark_configurations,
)
from .._job.spark_job_entry_mixin import SparkJobEntry, SparkJobEntryMixin
from .._util import convert_ordered_dict_to_dict, get_rest_dict_for_node_attrs, load_from_dict, validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Spark(BaseNode, SparkJobEntryMixin):
    """Base class for spark node, used for spark component version consumption.

    You should not instantiate this class directly. Instead, you should
    create it from the builder function: spark.

    :param component: The ID or instance of the Spark component or job to be run during the step.
    :type component: Union[str, ~azure.ai.ml.entities.SparkComponent]
    :param identity: The identity that the Spark job will use while running on compute.
    :type identity: Union[Dict[str, str],
        ~azure.ai.ml.entities.ManagedIdentityConfiguration,
        ~azure.ai.ml.entities.AmlTokenConfiguration,
        ~azure.ai.ml.entities.UserIdentityConfiguration

    ]

    :param driver_cores: The number of cores to use for the driver process, only in cluster mode.
    :type driver_cores: int
    :param driver_memory: The amount of memory to use for the driver process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :type driver_memory: str
    :param executor_cores: The number of cores to use on each executor.
    :type executor_cores: int
    :param executor_memory: The amount of memory to use per executor process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :type executor_memory: str
    :param executor_instances: The initial number of executors.
    :type executor_instances: int
    :param dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of
        executors registered with this application up and down based on the workload.
    :type dynamic_allocation_enabled: bool
    :param dynamic_allocation_min_executors: The lower bound for the number of executors if dynamic allocation
        is enabled.
    :type dynamic_allocation_min_executors: int
    :param dynamic_allocation_max_executors: The upper bound for the number of executors if dynamic allocation
        is enabled.
    :type dynamic_allocation_max_executors: int
    :param conf: A dictionary with pre-defined Spark configurations key and values.
    :type conf: Dict[str, str]
    :param inputs: A mapping of input names to input data sources used in the job.
    :type inputs: Dict[str, Union[
        str,
        bool,
        int,
        float,
        Enum,
        ~azure.ai.ml.entities._job.pipeline._io.NodeOutput,
        ~azure.ai.ml.Input

    ]]

    :param outputs: A mapping of output names to output data sources used in the job.
    :type outputs: Dict[str, Union[str, ~azure.ai.ml.Output]]
    :param args: The arguments for the job.
    :type args: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param resources: The compute resource configuration for the job.
    :type resources: Union[Dict, ~azure.ai.ml.entities.SparkResourceConfiguration]
    :param entry: The file or class entry point.
    :type entry: Dict[str, str]
    :param py_files: The list of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: List[str]
    :param jars: The list of .JAR files to include on the driver and executor classpaths.
    :type jars: List[str]
    :param files: The list of files to be placed in the working directory of each executor.
    :type files: List[str]
    :param archives: The list of archives to be extracted into the working directory of each executor.
    :type archives: List[str]
    """

    def __init__(
        self,
        *,
        component: Union[str, SparkComponent],
        identity: Optional[
            Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        driver_cores: Optional[Union[int, str]] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[Union[int, str]] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[Union[int, str]] = None,
        dynamic_allocation_enabled: Optional[Union[bool, str]] = None,
        dynamic_allocation_min_executors: Optional[Union[int, str]] = None,
        dynamic_allocation_max_executors: Optional[Union[int, str]] = None,
        conf: Optional[Dict[str, str]] = None,
        inputs: Optional[
            Dict[
                str,
                Union[
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
        compute: Optional[str] = None,
        resources: Optional[Union[Dict, SparkResourceConfiguration]] = None,
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        args: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        kwargs.pop("type", None)

        BaseNode.__init__(
            self, type=NodeType.SPARK, inputs=inputs, outputs=outputs, component=component, compute=compute, **kwargs
        )

        # init mark for _AttrDict
        self._init = True
        SparkJobEntryMixin.__init__(self, entry=entry)
        self.conf = conf
        self.driver_cores = driver_cores
        self.driver_memory = driver_memory
        self.executor_cores = executor_cores
        self.executor_memory = executor_memory
        self.executor_instances = executor_instances
        self.dynamic_allocation_enabled = dynamic_allocation_enabled
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors

        is_spark_component = isinstance(component, SparkComponent)
        if is_spark_component:
            # conf is dict and we need copy component conf here, otherwise node conf setting will affect component
            # setting
            _component = cast(SparkComponent, component)
            self.conf = self.conf or copy.copy(_component.conf)
            self.driver_cores = self.driver_cores or _component.driver_cores
            self.driver_memory = self.driver_memory or _component.driver_memory
            self.executor_cores = self.executor_cores or _component.executor_cores
            self.executor_memory = self.executor_memory or _component.executor_memory
            self.executor_instances = self.executor_instances or _component.executor_instances
            self.dynamic_allocation_enabled = self.dynamic_allocation_enabled or _component.dynamic_allocation_enabled
            self.dynamic_allocation_min_executors = (
                self.dynamic_allocation_min_executors or _component.dynamic_allocation_min_executors
            )
            self.dynamic_allocation_max_executors = (
                self.dynamic_allocation_max_executors or _component.dynamic_allocation_max_executors
            )
        if self.executor_instances is None and str(self.dynamic_allocation_enabled).lower() == "true":
            self.executor_instances = self.dynamic_allocation_min_executors
        # When create standalone job or pipeline job, following fields will always get value from component or get
        # default None, because we will not pass those fields to Spark. But in following cases, we expect to get
        # correct value from spark._from_rest_object() and then following fields will get from their respective
        # keyword arguments.
        # 1. when we call regenerated_spark_node=Spark._from_rest_object(spark_node._to_rest_object()) in local test,
        # we expect regenerated_spark_node and spark_node are identical.
        # 2.when get created remote job through Job._from_rest_object(result) in job operation where component is an
        # arm_id, we expect get remote returned values.
        # 3.when we load a remote job, component now is an arm_id, we need get entry from node level returned from
        # service
        self.entry = _component.entry if is_spark_component else entry
        self.py_files = _component.py_files if is_spark_component else py_files
        self.jars = _component.jars if is_spark_component else jars
        self.files = _component.files if is_spark_component else files
        self.archives = _component.archives if is_spark_component else archives
        self.args = _component.args if is_spark_component else args
        self.environment: Any = _component.environment if is_spark_component else None

        self.resources = resources
        self.identity = identity
        self._swept = False
        self._init = False

    @classmethod
    def _get_supported_outputs_types(cls) -> Tuple:
        return str, Output

    @property
    def component(self) -> Union[str, SparkComponent]:
        """The ID or instance of the Spark component or job to be run during the step.

        :rtype: ~azure.ai.ml.entities.SparkComponent
        """
        res: Union[str, SparkComponent] = self._component
        return res

    @property
    def resources(self) -> Optional[Union[Dict, SparkResourceConfiguration]]:
        """The compute resource configuration for the job.

        :rtype: ~azure.ai.ml.entities.SparkResourceConfiguration
        """
        return self._resources  # type: ignore

    @resources.setter
    def resources(self, value: Optional[Union[Dict, SparkResourceConfiguration]]) -> None:
        """Sets the compute resource configuration for the job.

        :param value: The compute resource configuration for the job.
        :type value: Union[Dict[str, str], ~azure.ai.ml.entities.SparkResourceConfiguration]
        """
        if isinstance(value, dict):
            value = SparkResourceConfiguration(**value)
        self._resources = value

    @property
    def identity(
        self,
    ) -> Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        """The identity that the Spark job will use while running on compute.

        :rtype: Union[~azure.ai.ml.entities.ManagedIdentityConfiguration, ~azure.ai.ml.entities.AmlTokenConfiguration,
            ~azure.ai.ml.entities.UserIdentityConfiguration]
        """
        # If there is no identity from CLI/SDK input: for jobs running on synapse compute (MLCompute Clusters), the
        # managed identity is the default; for jobs running on clusterless, the user identity should be the default,
        # otherwise use user input identity.
        if self._identity is None:
            if self.compute is not None:
                return ManagedIdentityConfiguration()
            if self.resources is not None:
                return UserIdentityConfiguration()
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration],
    ) -> None:
        """Sets the identity that the Spark job will use while running on compute.

        :param value: The identity that the Spark job will use while running on compute.
        :type value: Union[Dict[str, str], ~azure.ai.ml.entities.ManagedIdentityConfiguration,
            ~azure.ai.ml.entities.AmlTokenConfiguration, ~azure.ai.ml.entities.UserIdentityConfiguration]
        """
        if isinstance(value, dict):
            identify_schema = UnionField(
                [
                    NestedField(ManagedIdentitySchema, unknown=INCLUDE),
                    NestedField(AMLTokenIdentitySchema, unknown=INCLUDE),
                    NestedField(UserIdentitySchema, unknown=INCLUDE),
                ]
            )
            value = identify_schema._deserialize(value=value, attr=None, data=None)
        self._identity = value

    @property
    def code(self) -> Optional[Union[str, PathLike]]:
        """The local or remote path pointing at source code.

        :rtype: Union[str, PathLike]
        """
        if isinstance(self.component, Component):
            _code: Optional[Union[str, PathLike]] = self.component.code
            return _code
        return None

    @code.setter
    def code(self, value: str) -> None:
        """Sets the source code to be used for the job.

        :param value: The local or remote path pointing at source code.
        :type value: Union[str, PathLike]
        """
        if isinstance(self.component, Component):
            self.component.code = value
        else:
            msg = "Can't set code property for a registered component {}"
            raise ValidationException(
                message=msg.format(self.component),
                no_personal_data_message=msg.format(self.component),
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        obj = super()._from_rest_object_to_init_params(obj)

        if "resources" in obj and obj["resources"]:
            obj["resources"] = SparkResourceConfiguration._from_rest_object(obj["resources"])

        if "identity" in obj and obj["identity"]:
            obj["identity"] = _BaseJobIdentityConfiguration._from_rest_object(obj["identity"])

        if "entry" in obj and obj["entry"]:
            obj["entry"] = SparkJobEntry._from_rest_object(obj["entry"])
        if "conf" in obj and obj["conf"]:
            # get conf setting value from conf
            for field_name, _ in CONF_KEY_MAP.items():
                value = obj["conf"].get(field_name, None)
                if value is not None:
                    obj[field_name] = value

        return obj

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Spark":
        from .spark_func import spark

        loaded_data = load_from_dict(SparkJobSchema, data, context, additional_message, **kwargs)
        spark_job: Spark = spark(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return spark_job

    @classmethod
    def _load_from_rest_job(cls, obj: JobBaseData) -> "Spark":
        from .spark_func import spark

        rest_spark_job: RestSparkJob = obj.properties
        rest_spark_conf = copy.copy(rest_spark_job.conf) or {}

        spark_job: Spark = spark(
            name=obj.name,
            id=obj.id,
            entry=SparkJobEntry._from_rest_object(rest_spark_job.entry),
            display_name=rest_spark_job.display_name,
            description=rest_spark_job.description,
            tags=rest_spark_job.tags,
            properties=rest_spark_job.properties,
            experiment_name=rest_spark_job.experiment_name,
            services=rest_spark_job.services,
            status=rest_spark_job.status,
            creation_context=obj.system_data,
            code=rest_spark_job.code_id,
            compute=rest_spark_job.compute_id,
            environment=rest_spark_job.environment_id,
            identity=(
                _BaseJobIdentityConfiguration._from_rest_object(rest_spark_job.identity)
                if rest_spark_job.identity
                else None
            ),
            args=rest_spark_job.args,
            conf=rest_spark_conf,
            driver_cores=rest_spark_conf.get(
                SparkConfKey.DRIVER_CORES, None
            ),  # copy fields from conf into the promote attribute in spark
            driver_memory=rest_spark_conf.get(SparkConfKey.DRIVER_MEMORY, None),
            executor_cores=rest_spark_conf.get(SparkConfKey.EXECUTOR_CORES, None),
            executor_memory=rest_spark_conf.get(SparkConfKey.EXECUTOR_MEMORY, None),
            executor_instances=rest_spark_conf.get(SparkConfKey.EXECUTOR_INSTANCES, None),
            dynamic_allocation_enabled=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_ENABLED, None),
            dynamic_allocation_min_executors=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_MIN_EXECUTORS, None),
            dynamic_allocation_max_executors=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_MAX_EXECUTORS, None),
            resources=SparkResourceConfiguration._from_rest_object(rest_spark_job.resources),
            inputs=from_rest_inputs_to_dataset_literal(rest_spark_job.inputs),
            outputs=from_rest_data_outputs(rest_spark_job.outputs),
        )
        return spark_job

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            # hack: allow use InternalSparkComponent as component
            # "component": (str, SparkComponent),
            "environment": (str, Environment),
            "resources": (dict, SparkResourceConfiguration),
            "code": (str, PathLike),
        }

    @property
    def _skip_required_compute_missing_validation(self) -> bool:
        return self.resources is not None

    def _to_job(self) -> SparkJob:
        if isinstance(self.component, SparkComponent):
            return SparkJob(
                experiment_name=self.experiment_name,
                name=self.name,
                display_name=self.display_name,
                description=self.description,
                tags=self.tags,
                code=self.component.code,
                entry=self.entry,
                py_files=self.py_files,
                jars=self.jars,
                files=self.files,
                archives=self.archives,
                identity=self.identity,
                driver_cores=self.driver_cores,
                driver_memory=self.driver_memory,
                executor_cores=self.executor_cores,
                executor_memory=self.executor_memory,
                executor_instances=self.executor_instances,
                dynamic_allocation_enabled=self.dynamic_allocation_enabled,
                dynamic_allocation_min_executors=self.dynamic_allocation_min_executors,
                dynamic_allocation_max_executors=self.dynamic_allocation_max_executors,
                conf=self.conf,
                environment=self.environment,
                status=self.status,
                inputs=self._job_inputs,
                outputs=self._job_outputs,
                services=self.services,
                args=self.args,
                compute=self.compute,
                resources=self.resources,
            )

        return SparkJob(
            experiment_name=self.experiment_name,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            code=self.component,
            entry=self.entry,
            py_files=self.py_files,
            jars=self.jars,
            files=self.files,
            archives=self.archives,
            identity=self.identity,
            driver_cores=self.driver_cores,
            driver_memory=self.driver_memory,
            executor_cores=self.executor_cores,
            executor_memory=self.executor_memory,
            executor_instances=self.executor_instances,
            dynamic_allocation_enabled=self.dynamic_allocation_enabled,
            dynamic_allocation_min_executors=self.dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=self.dynamic_allocation_max_executors,
            conf=self.conf,
            environment=self.environment,
            status=self.status,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            services=self.services,
            args=self.args,
            compute=self.compute,
            resources=self.resources,
        )

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import SparkSchema

        return SparkSchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return [
            "type",
            "resources",
            "py_files",
            "jars",
            "files",
            "archives",
            "identity",
            "conf",
            "args",
        ]

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj: dict = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                {
                    "componentId": self._get_component_id(),
                    "identity": get_rest_dict_for_node_attrs(self.identity),
                    "resources": get_rest_dict_for_node_attrs(self.resources),
                    "entry": get_rest_dict_for_node_attrs(self.entry),
                }
            )
        )
        return rest_obj

    def _build_inputs(self) -> dict:
        inputs = super(Spark, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    def _customized_validate(self) -> MutableValidationResult:
        result = super()._customized_validate()
        if (
            isinstance(self.component, SparkComponent)
            and isinstance(self.component._environment, Environment)
            and self.component._environment.image is not None
        ):
            result.append_warning(
                yaml_path="environment.image",
                message=SPARK_ENVIRONMENT_WARNING_MESSAGE,
            )
        result.merge_with(self._validate_entry_exist())
        result.merge_with(self._validate_fields())
        return result

    def _validate_entry_exist(self) -> MutableValidationResult:
        is_remote_code = isinstance(self.code, str) and (
            self.code.startswith("git+")
            or self.code.startswith(REGISTRY_URI_FORMAT)
            or self.code.startswith(ARM_ID_PREFIX)
            or is_url(self.code)
            or bool(self.CODE_ID_RE_PATTERN.match(self.code))
        )
        validation_result = self._create_empty_validation_result()
        # validate whether component entry exists to ensure code path is correct, especially when code is default value
        if self.code is None or is_remote_code or not isinstance(self.entry, SparkJobEntry):
            # skip validate when code is not a local path or code is None, or self.entry is not SparkJobEntry object
            pass
        else:
            if not path.isabs(self.code):
                _component: SparkComponent = self.component  # type: ignore
                code_path = Path(_component.base_path) / self.code
                if code_path.exists():
                    code_path = code_path.resolve().absolute()
                else:
                    validation_result.append_error(
                        message=f"Code path {code_path} doesn't exist.", yaml_path="component.code"
                    )
                entry_path = code_path / self.entry.entry
            else:
                entry_path = Path(self.code) / self.entry.entry

            if (
                isinstance(self.entry, SparkJobEntry)
                and self.entry.entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY
            ):
                if not entry_path.exists():
                    validation_result.append_error(
                        message=f"Entry {entry_path} doesn't exist.", yaml_path="component.entry"
                    )
        return validation_result

    def _validate_fields(self) -> MutableValidationResult:
        validation_result = self._create_empty_validation_result()
        try:
            _validate_compute_or_resources(self.compute, self.resources)
        except ValidationException as e:
            validation_result.append_error(message=str(e), yaml_path="resources")
            validation_result.append_error(message=str(e), yaml_path="compute")

        try:
            _validate_input_output_mode(self.inputs, self.outputs)
        except ValidationException as e:
            msg = str(e)
            m = re.match(r"(Input|Output) '(\w+)'", msg)
            if m:
                io_type, io_name = m.groups()
                if io_type == "Input":
                    validation_result.append_error(message=msg, yaml_path=f"inputs.{io_name}")
                else:
                    validation_result.append_error(message=msg, yaml_path=f"outputs.{io_name}")

        try:
            _validate_spark_configurations(self)
        except ValidationException as e:
            validation_result.append_error(message=str(e), yaml_path="conf")

        try:
            self._validate_entry()
        except ValidationException as e:
            validation_result.append_error(message=str(e), yaml_path="entry")

        if self.args:
            try:
                validate_inputs_for_args(self.args, self.inputs)
            except ValidationException as e:
                validation_result.append_error(message=str(e), yaml_path="args")
        return validation_result

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "Spark":
        """Call Spark as a function will return a new instance each time.

        :return: A Spark object
        :rtype: Spark
        """
        if isinstance(self._component, Component):
            # call this to validate inputs
            node: Spark = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs:
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of output won't change
                if not isinstance(original_output, str):
                    setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            node._name = self.name
            node.compute = self.compute
            node.environment = copy.deepcopy(self.environment)
            node.resources = copy.deepcopy(self.resources)
            return node

        msg = "Spark can be called as a function only when referenced component is {}, currently got {}."
        raise ValidationException(
            message=msg.format(type(Component), self._component),
            no_personal_data_message=msg.format(type(Component), "self._component"),
            target=ErrorTarget.SPARK_JOB,
        )
