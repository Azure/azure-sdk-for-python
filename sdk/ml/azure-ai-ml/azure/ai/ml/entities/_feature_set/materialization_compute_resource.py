# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    MaterializationComputeResource as RestMaterializationComputeResource,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


@experimental
class _MaterializationComputeResource(RestTranslatableMixin):
    def __init__(self, *, instance_type: str, **kwargs):  # pylint: disable=unused-argument
        """
        :keyword instance_type: Specifies the instance type.
        :paramtype instance_type: str
        """
        self.instance_type = instance_type

    def _to_rest_object(self) -> RestMaterializationComputeResource:
        return RestMaterializationComputeResource(instance_type=self.instance_type)

    @classmethod
    def _from_rest_object(cls, obj: RestMaterializationComputeResource) -> "_MaterializationComputeResource":
        if not obj:
            return None
        return _MaterializationComputeResource(instance_type=obj.instance_type)
