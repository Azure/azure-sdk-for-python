# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union, Any

from azure.ai.ml._schema._deployment.batch.job_definition_schema import JobDefinitionSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.run_settings import RunSettings
from azure.ai.ml.entities._component.component import Component


class JobDefinition:
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
        job: Union[Component, str] = None,
        component : Union[Component, str] = None,
        type: str = None,
        settings: Dict[str, Any] = None,
        name: str = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.job = job
        self.component = component
        self.type = type
        self.settings = settings
        self.name = name 
        self.tags = tags
        self.description = description

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return JobDefinitionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
