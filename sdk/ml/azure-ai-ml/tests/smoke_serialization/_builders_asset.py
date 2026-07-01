# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for asset entities (Model, Environment, Data, Code).

Uses remote ``azureml://`` / image references so ``_to_rest_object`` does not need local file upload.
"""
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import Data, Environment, Model
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._assets.environment import BuildContext

_REMOTE = "azureml://datastores/workspaceblobstore/paths/smoke/"


def build_model_full():
    """Model with flavors, stage, tags and a remote path."""
    return Model(
        name="smoke-model",
        version="1",
        type=AssetTypes.CUSTOM_MODEL,
        path=_REMOTE + "model/",
        description="smoke model",
        tags={"tag1": "value1"},
        properties={"prop1": "value1"},
        stage="Production",
        flavors={"python_function": {"loader_module": "smoke.loader"}},
    )


def build_model_mlflow():
    """MLflow model variation."""
    return Model(
        name="smoke-model-mlflow",
        version="2",
        type=AssetTypes.MLFLOW_MODEL,
        path=_REMOTE + "mlflow-model/",
    )


def build_environment_image():
    """Environment from a docker image + conda spec."""
    return Environment(
        name="smoke-env-image",
        version="1",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        description="smoke env",
        tags={"tag1": "value1"},
        conda_file={
            "name": "smoke",
            "dependencies": ["python=3.10", {"pip": ["azure-ai-ml"]}],
        },
    )


def build_environment_build_context():
    """Environment from a build context (Dockerfile)."""
    return Environment(
        name="smoke-env-build",
        version="1",
        build=BuildContext(path=_REMOTE + "context/", dockerfile_path="Dockerfile"),
    )


def build_data_uri_folder():
    """Data asset of type uri_folder."""
    return Data(
        name="smoke-data-folder",
        version="1",
        path=_REMOTE + "data/",
        type=AssetTypes.URI_FOLDER,
        description="smoke data",
        tags={"tag1": "value1"},
    )


def build_data_uri_file():
    """Data asset of type uri_file."""
    return Data(
        name="smoke-data-file",
        version="1",
        path=_REMOTE + "data/file.csv",
        type=AssetTypes.URI_FILE,
    )


def build_data_mltable():
    """Data asset of type mltable."""
    return Data(
        name="smoke-data-mltable",
        version="1",
        path=_REMOTE + "mltable/",
        type=AssetTypes.MLTABLE,
    )


def build_code_full():
    """Code asset with a remote path."""
    return Code(
        name="smoke-code",
        version="1",
        path=_REMOTE + "code/",
        description="smoke code",
        tags={"tag1": "value1"},
    )


MODEL_BUILDERS = {
    "model_full": build_model_full,
    "model_mlflow": build_model_mlflow,
}

ENVIRONMENT_BUILDERS = {
    "environment_image": build_environment_image,
    "environment_build_context": build_environment_build_context,
}

DATA_BUILDERS = {
    "data_uri_folder": build_data_uri_folder,
    "data_uri_file": build_data_uri_file,
    "data_mltable": build_data_mltable,
}

CODE_BUILDERS = {
    "code_full": build_code_full,
}
