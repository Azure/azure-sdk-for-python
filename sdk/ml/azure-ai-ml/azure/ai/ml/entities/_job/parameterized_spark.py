# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import os
from typing import Dict, List, Optional, Union

from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._job.spark_job_entry import SparkJobEntry

from .._job.spark_job_entry_mixin import SparkJobEntryMixin

DUMMY_IMAGE = "conda/miniconda3"


class ParameterizedSpark(SparkJobEntryMixin):
    """Spark component that contains supporting parameters.

    :param code: The source code to run the job.
    :type code: str
    :param entry: Entry.
    :type entry: str
    :param py_files: List of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: list[str]
    :param jars: List of jars to include on the driver and executor classpaths.
    :type jars: list[str]
    :param files: List of files to be placed in the working directory of each executor.
    :type files: list[str]
    :param archives: List of archives to be extracted into the working directory of each executor.
    :type archives: list[str]
    :param conf: A dict with pre-defined spark configurations key and values.
    :type conf: dict
    :param environment: Azure ML environment to run the job in.
    :type environment: Union[str, azure.ai.ml.entities.Environment]
    :param args: Arguments for the job.
    :type args: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        code: Union[str, os.PathLike] = ".",
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        conf: Optional[Dict[str, str]] = None,
        environment: Optional[Union[str, Environment]] = None,
        args: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.code = code
        self.entry = entry
        self.py_files = py_files
        self.jars = jars
        self.files = files
        self.archives = archives
        self.conf = conf
        self._environment = environment
        self.args = args

    @property
    def environment(self):
        if isinstance(self._environment, Environment) and self._environment.image is None:
            return Environment(conda_file=self._environment.conda_file, image=DUMMY_IMAGE)
        return self._environment

    @environment.setter
    def environment(self, value):
        self._environment = value
