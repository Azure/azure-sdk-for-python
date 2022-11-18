# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union, Any

from azure.ai.ml._schema._deployment.batch.job_definition_schema import JobDefinitionSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._job.job import Job


class JobDefinition:
    """Job Definition entity

    :param type: Job definition type. Allowed value is: pipeline
    :type type: str
    :param name: Job name
    :type name: str
    :param job: Job definition
    :type job: Union[Job, str]
    :param component: Component definition
    :type component: Union[Component, str]
    :param settings: Job settings
    :type settings: Dict[str, Any]
    :param description: Job description.
    :type description: str
    :param tags: Job tags
    :type tags: Dict[str, Any]
    """

    def __init__(
        self,
        type: str, # pylint: disable=redefined-builtin
        name: str = None,
        job: Union[Job, str] = None,
        component : Union[Component, str] = None,
        settings: Dict[str, Any] = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        **kwargs, # pylint: disable=unused-argument
    ):
        self.type = type
        self.name = name
        self.job = job
        self.component = component
        self.settings = settings
        self.tags = tags
        self.description = description

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return JobDefinitionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
