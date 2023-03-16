# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---

from typing import Dict

from azure.ai.ml._restclient.v2023_04_01_preview.models import BaseEnvironmentId as RestBaseEnvironmentId
from azure.ai.ml._schema.assets.package.base_environment_source import BaseEnvironmentSourceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class BaseEnvironmentId:
    def __init__(self, type: str = None, resource_id: str = None):
        """Compute node information related to a AmlCompute Variables are only populated by the server, and will be
        ignored when sending a request."""

        self.type = type
        self.resource_id = resource_id

    @classmethod
    def _from_rest_object(cls, rest_obj: RestBaseEnvironmentId) -> "RestBaseEnvironmentId":
        return BaseEnvironmentId(type=rest_obj.base_environment_source_type, resource_id=rest_obj.resource_id)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return BaseEnvironmentSourceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self) -> RestBaseEnvironmentId:
        return RestBaseEnvironmentId(base_environment_source_type=self.type, resource_id=self.resource_id)
