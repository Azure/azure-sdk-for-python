# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Any, Tuple

from azure.ai.ml.entities import Model

from ._registry_utils import get_registry_model


def get_default_allowed_instance_type_for_hugging_face(
    model_details: Model, credential: Any
) -> Tuple[str, str]:
    hf_engines = model_details.properties.get("skuBasedEngineIds", None)
    deployment_config = model_details.properties.get("modelDeploymentConfig", None)
    default_instance_type = None
    allowed_instance_types = []
    if hf_engines:
        # hf engines and deployment_config are mutually exclusive
        # the presence of one implies the other does not exist
        hf_engines = hf_engines.split(",")
        if len(hf_engines) > 1:
            for engine_id in hf_engines:
                instance_type, instance_type_list = get_default_allowed_instance_type_from_model_engine(engine_id, credential)
                if "cpu" in engine_id:
                    default_instance_type = instance_type
                allowed_instance_types.append(instance_type_list)
        else:
            # if the model has only one engine, we can proceed with that as the default engine for SKU
            # selection
            default_instance_type, allowed_instance_types = get_default_allowed_instance_type_from_model_engine(hf_engines[0], credential)
    else:
        default_instance_type, allowed_instance_types = parse_deployment_config(deployment_config)
    return (default_instance_type, allowed_instance_types)


def parse_deployment_config(deployment_config: str):
    deployment_config = json.loads(deployment_config)
    allowed_instance_types = deployment_config["PipelineMetadata"]["PipelineDefinition"]["ec"]["AllowedInstanceTypes"]
    default_instance_type = deployment_config["PipelineMetadata"]["PipelineDefinition"]["ec"]["DefaultInstanceType"]

    return (default_instance_type, allowed_instance_types)


def get_default_allowed_instance_type_from_model_engine(engine_id: str, credential: Any):
    model_details = get_registry_model(
        credential,
        id=engine_id
    )
    deployment_config = model_details.properties.get("modelDeploymentConfig", None)
    return parse_deployment_config(deployment_config)