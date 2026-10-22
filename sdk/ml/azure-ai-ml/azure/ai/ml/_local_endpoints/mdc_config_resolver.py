# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os.path
from pathlib import Path
from typing import Any, Dict

from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.entities._deployment.data_collector import DataCollector


class MdcConfigResolver(object):
    """Represents the contents of mdc config and handles writing the mdc configuration to User's system.

    :param data_collector: model data collector entity
    :type data_collector: DataCollector
    """

    def __init__(
        self,
        data_collector: DataCollector,
    ):
        self.environment_variables: Dict = {}
        self.volumes: Dict = {}
        self.mdc_config: Any = None
        self.config_path = "/etc/mdc-config.json"
        self.local_config_name = "mdc-config.json"
        self._construct(data_collector)

    def _construct(self, data_collector: DataCollector) -> None:
        """Constructs the mdc configuration based on entity.

        :param data_collector: The data collector
        :type data_collector: DataCollector

        .. note::

            Internal use only.
        """
        if not data_collector.collections:
            return

        if len(data_collector.collections) <= 0:
            return

        sampling_percentage = int(data_collector.sampling_rate * 100) if data_collector.sampling_rate else 100

        self.mdc_config = {"collections": {}, "runMode": "local"}
        custom_logging_enabled = False
        for k, v in data_collector.collections.items():
            if v.enabled and v.enabled.lower() == "true":
                lower_k = k.lower()

                if lower_k not in ("request", "response"):
                    custom_logging_enabled = True

                self.mdc_config["collections"][lower_k] = {
                    "enabled": True,
                    "sampling_percentage": int(v.sampling_rate * 100) if v.sampling_rate else sampling_percentage,
                }

        if not custom_logging_enabled:
            self.mdc_config = None
            return

        if data_collector.request_logging and data_collector.request_logging.capture_headers:
            self.mdc_config["captureHeaders"] = data_collector.request_logging.capture_headers

    def write_file(self, directory_path: str) -> None:
        """Writes this mdc configuration to a file in provided directory.

        :param directory_path: absolute path of local directory to write Dockerfile.
        :type directory_path: str
        """
        if not self.mdc_config:
            return

        mdc_setting_path = str(Path(directory_path, self.local_config_name).resolve())
        with open(mdc_setting_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
            d = json.dumps(self.mdc_config)
            f.write(f"{d}")

        self.environment_variables = {"AZUREML_MDC_CONFIG_PATH": self.config_path}
        local_path = os.path.join(directory_path, self.local_config_name)

        self.volumes = {f"{local_path}:{self.config_path}:z": {local_path: {"bind": self.config_path}}}
