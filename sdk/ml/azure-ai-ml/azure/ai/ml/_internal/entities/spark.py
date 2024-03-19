# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional, Union

from marshmallow import Schema

from ..._schema import PathAwareSchema
from ...constants._job.job import RestSparkConfKey
from ...entities import Environment, SparkJobEntry
from ...entities._job.parameterized_spark import DUMMY_IMAGE, ParameterizedSpark
from ...entities._job.spark_job_entry_mixin import SparkJobEntryMixin
from .._schema.component import InternalSparkComponentSchema
from ..entities import InternalComponent
from .environment import InternalEnvironment


class InternalSparkComponent(
    InternalComponent, ParameterizedSpark, SparkJobEntryMixin
):  # pylint: disable=too-many-instance-attributes, too-many-ancestors
    """Internal Spark Component
    This class is used to handle internal spark component.
    It can be loaded from internal spark component yaml or from rest object of an internal spark component.
    But after loaded, its structure will be the same as spark component.
    """

    def __init__(
        self,
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        driver_cores: Optional[int] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[int] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[int] = None,
        dynamic_allocation_enabled: Optional[bool] = None,
        dynamic_allocation_min_executors: Optional[int] = None,
        dynamic_allocation_max_executors: Optional[int] = None,
        conf: Optional[Dict[str, str]] = None,
        args: Optional[str] = None,
        **kwargs,
    ):
        SparkJobEntryMixin.__init__(self, entry=entry, **kwargs)
        # environment.setter has been overridden in ParameterizedSpark, so we need to pop it out here
        environment = kwargs.pop("environment", None)
        InternalComponent.__init__(self, **kwargs)
        # Pop it to avoid passing multiple values for code in ParameterizedSpark.__init__
        code = kwargs.pop("code", None)
        ParameterizedSpark.__init__(
            self,
            code=self.base_path,
            entry=entry,
            py_files=py_files,
            jars=jars,
            files=files,
            archives=archives,
            conf=conf,
            environment=environment,
            args=args,
            **kwargs,
        )
        self.code = code
        # For pipeline spark job, we also allow user to set driver_cores, driver_memory and so on by setting conf.
        # If root level fields are not set by user, we promote conf setting to root level to facilitate subsequent
        # verification. This usually happens when we use to_component(SparkJob) or builder function spark() as a node
        # in pipeline sdk
        conf = conf or {}
        self.driver_cores = driver_cores or conf.get(RestSparkConfKey.DRIVER_CORES, None)
        self.driver_memory = driver_memory or conf.get(RestSparkConfKey.DRIVER_MEMORY, None)
        self.executor_cores = executor_cores or conf.get(RestSparkConfKey.EXECUTOR_CORES, None)
        self.executor_memory = executor_memory or conf.get(RestSparkConfKey.EXECUTOR_MEMORY, None)
        self.executor_instances = executor_instances or conf.get(RestSparkConfKey.EXECUTOR_INSTANCES, None)
        self.dynamic_allocation_enabled = dynamic_allocation_enabled or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_ENABLED, None
        )
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_MIN_EXECUTORS, None
        )
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_MAX_EXECUTORS, None
        )

        self.conf = conf
        self.args = args

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalSparkComponentSchema(context=context)

    @property  # type: ignore[override]
    def environment(self) -> Optional[Union[Environment, str]]:
        """Get the environment of the component.

        :return: The environment of the component.
        :rtype: Optional[Union[Environment, str]]]
        """
        if isinstance(self._environment, Environment) and self._environment.image is None:
            return Environment(conda_file=self._environment.conda_file, image=DUMMY_IMAGE)
        return self._environment

    @environment.setter
    def environment(self, value):
        """Set the environment of the component.

        :param value: The environment of the component.
        :type value: Union[str, Environment, dict]
        :return: No return
        :rtype: None
        """
        if value is None or isinstance(value, (str, Environment)):
            self._environment = value
        elif isinstance(value, dict):
            internal_environment = InternalEnvironment(**value)
            internal_environment.resolve(self.base_path)
            self._environment = Environment(
                name=internal_environment.name,
                version=internal_environment.version,
            )
            if internal_environment.conda:
                self._environment.conda_file = {
                    "dependencies": internal_environment.conda[InternalEnvironment.CONDA_DEPENDENCIES]
                }
            if internal_environment.docker:
                self._environment.image = internal_environment.docker["image"]
            # we suppose that loaded internal spark component won't be used to create another internal spark component
            # so the environment construction here can be simplified
        else:
            raise ValueError(f"Unsupported environment type: {type(value)}")

    @property
    def jars(self) -> Optional[List[str]]:
        """Get the jars of the component.

        :return: The jars of the component.
        :rtype: Optional[List[str]]
        """
        return self._jars

    @jars.setter
    def jars(self, value: Union[str, List[str]]):
        """Set the jars of the component.

        :param value: The jars of the component.
        :type value: Union[str, List[str]]
        :return: No return
        :rtype: None
        """
        if isinstance(value, str):
            value = [value]
        self._jars = value

    @property
    def py_files(self) -> Optional[List[str]]:
        """Get the py_files of the component.

        :return: The py_files of the component.
        :rtype: Optional[List[str]]
        """
        return self._py_files

    @py_files.setter
    def py_files(self, value):
        """Set the py_files of the component.

        :param value: The py_files of the component.
        :type value: Union[str, List[str]]
        :return: No return
        :rtype: None
        """
        if isinstance(value, str):
            value = [value]
        self._py_files = value

    def _to_dict(self) -> Dict:
        result = super()._to_dict()
        return result

    def _to_rest_object(self):
        result = super()._to_rest_object()
        if "pyFiles" in result.properties.component_spec:
            result.properties.component_spec["py_files"] = result.properties.component_spec.pop("pyFiles")
        return result

    @classmethod
    def _from_rest_object_to_init_params(cls, obj) -> Dict:
        if "py_files" in obj.properties.component_spec:
            obj.properties.component_spec["pyFiles"] = obj.properties.component_spec.pop("py_files")
        result = super()._from_rest_object_to_init_params(obj)
        return result
