# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Dict, Any
from ._identity import IdentityConfiguration
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, ComputeType, TYPE
from azure.ai.ml.entities import Compute
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._schema.compute.kubernetes_compute import KubernetesComputeSchema
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ComputeResource,
    KubernetesProperties,
    Kubernetes,
)


class KubernetesCompute(Compute):
    """Kubernetes Compute resource

    :param name: Name of the compute
    :type name: str
    :param location: The resource location, defaults to None
    :type location: Optional[str], optional
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param resource_id: ARM resource id of the underlying compute, defaults to None
    :type resource_id: Optional[str], optional
    :param created_on: defaults to None
    :type created_on: Optional[str], optional
    :param provisioning_state: defaults to None
    :type provisioning_state: Optional[str], optional
    :param namespace: Namespace of the KubernetesCompute
    :type namespace: Optional[str], optional
    :param properties: KubernetesProperties, defaults to None
    :type properties: Optional[Dict], optional
    :param identity:  The identity configuration, identities that are associated with the compute cluster.
    :type identity: IdentityConfiguration, optional
    """

    def __init__(
        self,
        *,
        namespace: Optional[str] = "default",
        properties: Optional[Dict[str, Any]] = None,
        identity: IdentityConfiguration = None,
        **kwargs,
    ):
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
            provisioning_state=prop.provisioning_state,
            provisioning_errors=prop.provisioning_errors[0].error.code
            if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
            else None,
            created_on=prop.additional_properties.get("createdOn", None),
            properties=prop.properties.as_dict() if prop.properties else None,
            namespace=prop.properties.namespace,
            identity=IdentityConfiguration._from_rest_object(rest_obj.identity) if rest_obj.identity else None,
        )

    def _to_dict(self) -> Dict:
        return KubernetesComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "KubernetesCompute":
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
            identity=(self.identity._to_rest_object() if self.identity else None),
        )
