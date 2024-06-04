# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union

from azure.ai.ml._schema._deployment.batch.job_definition_schema import JobDefinitionSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._job.job import Job


@experimental
class JobDefinition:
    """Job Definition entity.

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
        # pylint: disable=redefined-builtin
        type: str,
        name: Optional[str] = None,
        job: Optional[Union[Job, str]] = None,
        component: Optional[Union[Component, str]] = None,
        settings: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        # pylint: disable=unused-argument
        **kwargs: Any,
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
        res: dict = JobDefinitionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
