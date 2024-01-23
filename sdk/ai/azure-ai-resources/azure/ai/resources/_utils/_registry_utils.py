# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Optional

REGISTRY_VERSIONED_ID_REGEX = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
REGISTRY_LABEL_ID_REGEX = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/labels/([^/]+)"


def get_registry_model(
    credential,
    registry_name: Optional[str] = None,
    id: Optional[str] = None,
    model_name: Optional[str] = None,
    version: Optional[str] = None,
    label: Optional[str] = None,
):
    from azure.ai.ml import MLClient

    if id:
        if "versions" in id:
            match = re.match(REGISTRY_VERSIONED_ID_REGEX, id)
            registry_name = match.group(1)  # type: ignore[union-attr]
            model_name = match.group(3)  # type: ignore[union-attr]
            version = match.group(4)  # type: ignore[union-attr]
        elif "labels" in id:
            match = re.match(REGISTRY_LABEL_ID_REGEX, id)
            registry_name = match.group(1)  # type: ignore[union-attr]
            model_name = match.group(3)  # type: ignore[union-attr]
            label = match.group(4)  # type: ignore[union-attr]

    registry_client = MLClient(credential, registry_name=registry_name)
    return registry_client.models.get(name=model_name, label=label, version=version)
