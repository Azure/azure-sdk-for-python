# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

REGISTRY_VERSIONED_ID_REGEX = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
REGISTRY_LABEL_ID_REGEX = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/labels/([^/]+)"


def get_registry_model(
    registry_name: str,
    credential,
    id: str = None,
    model_name: str = None,
    version: str = None,
    label: str = None,
):
    from azure.ai.ml import MLClient

    registry_client = MLClient(credential, registry_name=registry_name)

    if id:
        if "versions" in id:
            match = re.match(REGISTRY_VERSIONED_ID_REGEX, id)
            model_name = match.group(3)
            version = match.group(4)
        elif "labels" in id:
            match = re.match(REGISTRY_LABEL_ID_REGEX, id)
            model_name = match.group(3)
            label = match.group(4)

    return registry_client.models.get(name=model_name, label=label, version=version)
