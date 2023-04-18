# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin

from typing import Dict

from azure.ai.ml._restclient.v2023_02_01_preview.models import BaseEnvironmentId as RestBaseEnvironmentId
from azure.ai.ml._schema.assets.package.base_environment_source import BaseEnvironmentSourceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._utils._experimental import experimental


@experimental
class BaseEnvironment:
    """Base environment type.

    All required parameters must be populated in order to send to Azure.

    :param type: The type of the base environment.
    :type type: str
    :param resource_id: The resource id of the base environment. e.g. azureml:<name>:<version>
    :type resource_id: str

    """

    def __init__(self, type, resource_id: str = None):
        self.type = type
        self.resource_id = resource_id

    @classmethod
    def _from_rest_object(cls, rest_obj: RestBaseEnvironmentId) -> "RestBaseEnvironmentId":
        return BaseEnvironment(type=rest_obj.base_environment_source_type, resource_id=rest_obj.resource_id)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BaseEnvironmentSourceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self) -> RestBaseEnvironmentId:
        return RestBaseEnvironmentId(base_environment_source_type=self.type, resource_id=self.resource_id)
