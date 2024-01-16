# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import os
from typing import Any, Dict, List, Optional, Union

from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._job.spark_job_entry import SparkJobEntry

from .._job.spark_job_entry_mixin import SparkJobEntryMixin

DUMMY_IMAGE = "conda/miniconda3"


class ParameterizedSpark(SparkJobEntryMixin):
    """
    This class should not be instantiated directly. Instead, use the child class ~azure.ai.ml.entities.SparkComponent.

    Spark component that contains supporting parameters.

    :param code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url pointing
        to a remote location.
    :type code: Optional[Union[str, os.PathLike]]
    :param entry: The file or class entry point.
    :type entry: dict[str, str]
    :param py_files: The list of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: Optional[list[str]]
    :param jars: The list of .JAR files to include on the driver and executor classpaths.
    :type jars: Optional[list[str]]
    :param files: The list of files to be placed in the working directory of each executor.
    :type files: Optional[list[str]]
    :param archives: The list of archives to be extracted into the working directory of each executor.
    :type archives: Optional[list[str]]
    :param conf: A dictionary with pre-defined Spark configurations key and values.
    :type conf: Optional[dict[str, str]]
    :param environment: The Azure ML environment to run the job in.
    :type environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :param args: The arguments for the job.
    :type args: Optional[str]
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict
    """

    def __init__(
        self,
        code: Optional[Union[str, os.PathLike]] = ".",
        entry: Optional[Union[Dict[str, str], SparkJobEntry]] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        conf: Optional[Dict[str, str]] = None,
        environment: Optional[Union[str, Environment]] = None,
        args: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.args = None

        super().__init__(**kwargs)
        self.code = code
        self.entry = entry
        self.py_files = py_files
        self.jars = jars
        self.files = files
        self.archives = archives
        self.conf = conf
        self.environment = environment
        self.args = args

    @property
    def environment(self) -> Optional[Union[str, Environment]]:
        """The Azure ML environment to run the Spark component or job in.

        :return: The Azure ML environment to run the Spark component or job in.
        :rtype: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
        """
        if isinstance(self._environment, Environment) and self._environment.image is None:
            return Environment(conda_file=self._environment.conda_file, image=DUMMY_IMAGE)
        return self._environment

    @environment.setter
    def environment(self, value: Optional[Union[str, Environment]]) -> None:
        """Sets the Azure ML environment to run the Spark component or job in.

        :param value: The Azure ML environment to run the Spark component or job in.
        :type value: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
        """
        self._environment = value
