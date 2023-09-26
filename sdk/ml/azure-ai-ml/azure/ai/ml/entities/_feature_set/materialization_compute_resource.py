# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MaterializationComputeResource as RestMaterializationComputeResource,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin


@experimental
class MaterializationComputeResource(RestTranslatableMixin):
    """Materialization Compute resource

    :keyword instance_type: The compute instance type.
    :paramtype instance_type: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START materialization_compute_resource]
            :end-before: [END materialization_compute_resource]
            :language: python
            :dedent: 8
            :caption: Creating a MaterializationComputeResource object.
    """

    def __init__(self, *, instance_type: str, **kwargs):  # pylint: disable=unused-argument
        self.instance_type = instance_type

    def _to_rest_object(self) -> RestMaterializationComputeResource:
        return RestMaterializationComputeResource(instance_type=self.instance_type)

    @classmethod
    def _from_rest_object(cls, obj: RestMaterializationComputeResource) -> "MaterializationComputeResource":
        if not obj:
            return None
        return MaterializationComputeResource(instance_type=obj.instance_type)
