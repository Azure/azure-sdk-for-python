# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict

from azure.ai.ml._schema._deployment.batch.run_settings_schema import RunSettingsSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

class RunSettings:
    """Run Settings entity

    :param name: Run settings name
    :type name: str
    :param display_name: Run settings display name
    :type display_name: str
    :param experiment_name: Run settings experiment name
    :type experiment_name: str
    :param description: Run settings description
    :type description: str
    :param tags: Run settings tags
    :type tags: Dict[str, Any]
    :param settings: Run settings - settings
    :type settings: Dict[str, Any]
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