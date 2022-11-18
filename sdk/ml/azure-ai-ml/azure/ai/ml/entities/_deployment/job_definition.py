# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union, Any

from azure.ai.ml._schema._deployment.batch.job_definition_schema import JobDefinitionSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._component.component import Component


class JobDefinition:
    """Job Definition entity

    :param name: Job name
    :type name: str
    :param job: Job definition
    :type job: Union[Component, str]
    :param component: Component definition
    :type component: Union[Component, str]
    :param type: Job definition type
    :type type: str
    :param settings: Job settings
    :type settings: Dict[str, Any]
    :param description: Job description
    :type description: str
    :param tags: Job tags
    :type tags: Dict[str, Any]
    """

    def __init__(
        self,
        name: str = None,
        job: Union[Component, str] = None,
        component : Union[Component, str] = None,
        type: str = None, # pylint: disable=redefined-builtin
        settings: Dict[str, Any] = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        **kwargs, # pylint: disable=unused-argument
    ):
        self.name = name
        self.job = job
        self.component = component
        self.type = type
        self.settings = settings
        self.tags = tags
        self.description = description

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return JobDefinitionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
