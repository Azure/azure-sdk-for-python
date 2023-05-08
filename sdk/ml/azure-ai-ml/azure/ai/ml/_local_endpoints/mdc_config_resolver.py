# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from pathlib import Path

from azure.ai.ml.entities._deployment.data_collector import DataCollector


class MdcConfigResolver(object):
    def __init__(
        self,
        data_collector: DataCollector,
    ):
        self.environment_variables = None
        self.volumes = None
        self.mdc_config = None
        self._construct(data_collector)

    def _construct(self, data_collector: DataCollector) -> None:
        if not data_collector.collections:
            return

        if len(data_collector.collections) <= 0:
            return

        sampling_percentage = 100
        if data_collector.sampling_rate:
            sampling_percentage = int(data_collector.sampling_rate * 100)

        self.mdc_config = {"collections": {}, "runMode": "local"}
        for k, v in data_collector.collections:
            if v.enabled:
                lower_k = k.lower()
                self.mdc_config["collections"][lower_k] = {
                    "enabled": True,
                    "sampling_percentage": sampling_percentage,
                }

        if data_collector.request_logging and data_collector.request_logging.capture_headers:
            self.mdc_config["captureHeaders"] = data_collector.request_logging.capture_headers

    def write_file(self, directory_path: str) -> None:
        if not self.mdc_config:
            return

        mdc_setting_path = str(Path(directory_path, "mdc_config.json").resolve())
        with open(mdc_setting_path, "w") as f:
            d = json.dumps(self.mdc_config)
            f.write(f"{d}")

        self.environment_variables = {"AZUREML_MDC_CONFIG_PATH": "/etc/mdc-config.json"}
        self.volumes = {
            f"{directory_path}/mdc_config.json:/etc:z": {
                f"{directory_path}/mdc_config.json": {"bind": "/etc/mdc-config.json"}
            }
        }
