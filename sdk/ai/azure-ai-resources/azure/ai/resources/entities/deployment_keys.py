# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass

from azure.ai.ml.entities import EndpointAuthKeys

@dataclass
class DeploymentKeys:
    """Keys for model deployments

    :param primary_key: The primary key for the deployment.
    :type primary_key: str
    :param secondary_key: The secondary key for the deployment.
    :type secondary_key: str
    """
    primary_key: str
    secondary_key: str

    @classmethod
    def _from_v2_endpoint_keys(cls, keys: EndpointAuthKeys) -> "DeploymentKeys":
        return cls(
            primary_key=keys.primary_key,
            secondary_key=keys.secondary_key,
        )
