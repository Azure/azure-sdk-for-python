# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.batch.run_settings_schema import RunSettingsSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from typing import Any, Dict

class RunSettings:
    """Data Capture deployment entity

    :param enabled: Is data capture enabled.
    :type enabled: bool
    :param rolling_rate: The rolling rate of mdc files, possible values: ["year", "month", "day", "hour", "minute"].
    :type rolling_rate: str
    :param destination: Must be blob store.
    :type destination: Destination
    :param sampling_strategy: Sample percent of traffic.
    :type sampling_strategy: SamplingStrategy, optional
    :param request_logging: Logging of request payload parameters.
    :type request_logging: RequestLogging
    """

    def __init__(
        self,
        name: str = None,
        display_name: str = None,
        experiment_name: str = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        settings: Dict[str, Any] = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.name = name
        self.display_name = display_name
        self.experiment_name = experiment_name
        self.description = description
        self.tags = tags
        self.settings = settings

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return RunSettingsSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
