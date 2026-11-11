# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin

from typing import Any, Dict, Optional

from azure.ai.ml._schema.assets.package.base_environment_source import BaseEnvironmentSourceSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


@experimental
class BaseEnvironment:
    """Base environment type.

    All required parameters must be populated in order to send to Azure.

    :param type: The type of the base environment.
    :type type: str
    :param resource_id: The resource id of the base environment. e.g. azureml:name:version
    :type resource_id: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START base_env_entity_create]
            :end-before: [END base_env_entity_create]
            :language: python
            :dedent: 8
            :caption: Create a Base Environment object.
    """

    def __init__(self, type: str, resource_id: Optional[str] = None):
        self.type = type
        self.resource_id = resource_id

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "BaseEnvironment":
        if isinstance(rest_obj, dict):
            return BaseEnvironment(
                type=rest_obj.get("baseEnvironmentSourceType"),  # type: ignore[arg-type]
                resource_id=rest_obj.get("resourceId"),
            )
        return BaseEnvironment(type=rest_obj.base_environment_source_type, resource_id=rest_obj.resource_id)

    def _to_dict(self) -> Dict:
        return dict(BaseEnvironmentSourceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"baseEnvironmentSourceType": self.type}
        if self.resource_id is not None:
            rest["resourceId"] = self.resource_id
        return rest
