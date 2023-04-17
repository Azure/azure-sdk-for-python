# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-instance-attributes

import copy
import logging
from enum import Enum
from os import PathLike, path
from pathlib import Path
from typing import Dict, List, Optional, Union

from marshmallow import INCLUDE, Schema

from ..._restclient.v2023_04_01_preview.models import JobBase as JobBaseData
from ..._restclient.v2023_04_01_preview.models import SparkJob as RestSparkJob
from ..._schema import NestedField, PathAwareSchema, UnionField
from ..._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from ..._schema.job.parameterized_spark import CONF_KEY_MAP, SparkConfSchema
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
    create from builder function: spark.

    :param component: Id or instance of the spark component/job to be run for the step
    :type component: SparkComponent
    :param entry: File or class entry point.
    :type entry: dict[str, str]
    :param py_files: List of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: Optional[typing.List[str]]
    :param jars: List of jars to include on the driver and executor classpaths.
    :type jars: Optional[typing.List[str]]
    :param files: List of files to be placed in the working directory of each executor.
    :type files: Optional[typing.List[str]]
    :param archives: List of archives to be extracted into the working directory of each executor.
    :type archives: Optional[typing.List[str]]
    :param identity: Identity that spark job will use while running on compute.
    :type identity: Union[
        Dict,
        ManagedIdentityConfiguration,
        AmlTokenConfiguration,
        UserIdentityConfiguration]
    :param driver_cores: Number of cores to use for the driver process, only in cluster mode.
    :type driver_cores: int
    :param driver_memory: Amount of memory to use for the driver process.
    :type driver_memory: str
    :param executor_cores: The number of cores to use on each executor.
    :type executor_cores: int
    :param executor_memory: Amount of memory to use per executor process, in the same format as JVM memory strings with
        a size unit suffix ("k", "m", "g" or "t") (e.g. 512m, 2g).
    :type executor_memory: str
    :param executor_instances: Initial number of executors.
    :type executor_instances: int
    :param dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of executors
        registered with this application up and down based on the workload.
    :type dynamic_allocation_enabled: bool
    :param dynamic_allocation_min_executors: Lower bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_min_executors: int
    :param dynamic_allocation_max_executors: Upper bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_max_executors: int
    :param conf: A dict with pre-defined spark configurations key and values.
    :type conf: dict
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    :param args: Arguments for the job.
    :type args: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param resources: Compute Resource configuration for the job.
    :type resources: Union[Dict, SparkResourceConfiguration]
    """

    def __init__(
        self,
        *,
        component: Union[str, SparkComponent],
        identity: Optional[
            Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        driver_cores: Optional[int] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[int] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[int] = None,
        dynamic_allocation_enabled: Optional[bool] = None,
        dynamic_allocation_min_executors: Optional[int] = None,
        dynamic_allocation_max_executors: Optional[int] = None,
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
        **kwargs,
    ):
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
            self.conf = self.conf or copy.copy(component.conf)
            self.driver_cores = self.driver_cores or component.driver_cores
            self.driver_memory = self.driver_memory or component.driver_memory
            self.executor_cores = self.executor_cores or component.executor_cores
            self.executor_memory = self.executor_memory or component.executor_memory
            self.executor_instances = self.executor_instances or component.executor_instances
            self.dynamic_allocation_enabled = self.dynamic_allocation_enabled or component.dynamic_allocation_enabled
            self.dynamic_allocation_min_executors = (
                self.dynamic_allocation_min_executors or component.dynamic_allocation_min_executors
            )
            self.dynamic_allocation_max_executors = (
                self.dynamic_allocation_max_executors or component.dynamic_allocation_max_executors
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
        self.entry = component.entry if is_spark_component else entry
        self.py_files = component.py_files if is_spark_component else py_files
        self.jars = component.jars if is_spark_component else jars
        self.files = component.files if is_spark_component else files
        self.archives = component.archives if is_spark_component else archives
        self.args = component.args if is_spark_component else args
        self.environment = component.environment if is_spark_component else None

        self.resources = resources
        self.identity = identity
        self._swept = False
        self._init = False

    @classmethod
    def _get_supported_outputs_types(cls):
        return str, Output

    @property
    def component(self) -> Union[str, SparkComponent]:
        return self._component

    @property
    def resources(self) -> Optional[SparkResourceConfiguration]:
        """Compute Resource configuration for the job."""

        return self._resources

    @resources.setter
    def resources(self, value: Union[Dict[str, str], SparkResourceConfiguration, None]):
        if isinstance(value, dict):
            value = SparkResourceConfiguration(**value)
        self._resources = value

    @property
    def identity(
        self,
    ) -> Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        """Identity that spark job will use while running on compute."""
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
        value: Union[
            Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, None
        ],
    ):
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
        return self.component.code if hasattr(self.component, "code") else None

    @code.setter
    def code(self, value: str) -> None:
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
            identify_schema = UnionField(
                [
                    NestedField(SparkConfSchema, unknown=INCLUDE),
                ]
            )
            obj["conf"] = identify_schema._deserialize(value=obj["conf"], attr=None, data=None)

            # get conf setting value from conf
            for field_name, _ in CONF_KEY_MAP.items():
                value = obj["conf"].get(field_name, None)
                if value is not None:
                    obj[field_name] = value

        return obj

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Spark":
        from .spark_func import spark

        loaded_data = load_from_dict(SparkJobSchema, data, context, additional_message, **kwargs)
        spark_job = spark(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return spark_job

    @classmethod
    def _load_from_rest_job(cls, obj: JobBaseData) -> "Spark":
        from .spark_func import spark

        rest_spark_job: RestSparkJob = obj.properties
        identify_schema = UnionField(
            [
                NestedField(SparkConfSchema, unknown=INCLUDE),
            ]
        )
        rest_spark_conf = copy.copy(rest_spark_job.conf) or {}
        rest_spark_conf = identify_schema._deserialize(value=rest_spark_conf, attr=None, data=None)

        spark_job = spark(
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
            identity=_BaseJobIdentityConfiguration._from_rest_object(rest_spark_job.identity)
            if rest_spark_job.identity
            else None,
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
    def _skip_required_compute_missing_validation(self):
        return self.resources is not None

    def _to_job(self) -> SparkJob:
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

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
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

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                dict(
                    componentId=self._get_component_id(),
                    identity=get_rest_dict_for_node_attrs(self.identity),
                    resources=get_rest_dict_for_node_attrs(self.resources),
                    entry=get_rest_dict_for_node_attrs(self.entry),
                )
            )
        )
        return rest_obj

    def _build_inputs(self):
        inputs = super(Spark, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    def _customized_validate(self):
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
        result.merge_with(self._validate_entry_exist(raise_error=False))
        try:
            self._validate_fields()
        except ValidationException as e:
            result.append_error(yaml_path="*", message=str(e))
        return result

    def _validate_entry_exist(self, raise_error=False) -> MutableValidationResult:
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
                code_path = Path(self.component.base_path) / self.code
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
        return validation_result.try_raise(error_target=self._get_validation_error_target(), raise_error=raise_error)

    def _validate_fields(self) -> None:
        _validate_compute_or_resources(self.compute, self.resources)
        _validate_input_output_mode(self.inputs, self.outputs)
        _validate_spark_configurations(self)
        self._validate_entry()

        if self.args:
            validate_inputs_for_args(self.args, self.inputs)

    def __call__(self, *args, **kwargs) -> "Spark":
        """Call Spark as a function will return a new instance each time."""
        if isinstance(self._component, Component):
            # call this to validate inputs
            node = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs.keys():
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of output won't change
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
