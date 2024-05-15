# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource, Kubernetes, KubernetesProperties
from azure.ai.ml._schema.compute.kubernetes_compute import KubernetesComputeSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._util import load_from_dict


class KubernetesCompute(Compute):
    """Kubernetes Compute resource.

    :param namespace: The namespace of the KubernetesCompute. Defaults to "default".
    :type namespace: Optional[str]
    :param properties: The properties of the Kubernetes compute resource.
    :type properties: Optional[Dict]
    :param identity: The identities that are associated with the compute cluster.
    :type identity: ~azure.ai.ml.entities.IdentityConfiguration

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START kubernetes_compute]
            :end-before: [END kubernetes_compute]
            :language: python
            :dedent: 8
            :caption: Creating a KubernetesCompute object.
    """

    def __init__(
        self,
        *,
        namespace: str = "default",
        properties: Optional[Dict[str, Any]] = None,
        identity: Optional[IdentityConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = ComputeType.KUBERNETES
        super().__init__(**kwargs)
        self.namespace = namespace
        self.properties = properties if properties else {}
        if "properties" in self.properties:
            self.properties["properties"]["namespace"] = namespace
        self.identity = identity

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "KubernetesCompute":
        prop = rest_obj.properties
        return KubernetesCompute(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            tags=rest_obj.tags if rest_obj.tags else None,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=(
                prop.provisioning_errors[0].error.code
                if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
                else None
            ),
            created_on=prop.additional_properties.get("createdOn", None),
            properties=prop.properties.as_dict() if prop.properties else None,
            namespace=prop.properties.namespace,
            identity=IdentityConfiguration._from_compute_rest_object(rest_obj.identity) if rest_obj.identity else None,
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = KubernetesComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "KubernetesCompute":
        if not data:
            data = {"namespace": "default"}
        if "namespace" not in data:
            data["namespace"] = "default"

        loaded_data = load_from_dict(KubernetesComputeSchema, data, context, **kwargs)
        return KubernetesCompute(**loaded_data)

    def _to_rest_object(self) -> ComputeResource:
        kubernetes_prop = KubernetesProperties.from_dict(self.properties)
        kubernetes_prop.namespace = self.namespace
        kubernetes_comp = Kubernetes(
            resource_id=self.resource_id,
            compute_location=self.location,
            description=self.description,
            properties=kubernetes_prop,
        )
        return ComputeResource(
            location=self.location,
            properties=kubernetes_comp,
            name=self.name,
            identity=(self.identity._to_compute_rest_object() if self.identity else None),
            tags=self.tags,
        )
