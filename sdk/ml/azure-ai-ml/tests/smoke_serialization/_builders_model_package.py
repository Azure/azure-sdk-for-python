# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for model-package entities (smoke serialization suite).

``ModelPackage`` is the ``@experimental`` model-packaging request entity. The migration rewrote this
tree off the msrest ``PackageRequest`` base class (``ModelPackage(Resource, PackageRequest)`` ->
``ModelPackage(Resource)``) so that ``_to_rest_object()`` now hand-builds the camelCase wire ``dict``
directly instead of relying on msrest ``.serialize()``. That makes it exactly the kind of entity whose
wire must be pinned byte-for-byte against the pre-migration baseline.

``_to_rest_object()`` here already returns a plain ``dict`` (both on baseline via msrest
``.serialize()`` and on the branch via the hand-built dict), which ``serialize_wire`` handles.

NOTE: ``tags`` are intentionally NOT set on these builders. Pre-migration, ``ModelPackage(Resource,
PackageRequest)`` silently swallowed the ``tags`` kwarg through its diamond MRO (``entity.tags`` stayed
``None``), so tags were never sent. The migration's ``ModelPackage(Resource)`` now honors ``tags`` -- a
latent bug-fix, not a wire regression -- but it does change the wire *when* tags are set. These
builders pin the substantive package wire (which is preserved byte-for-byte); the tags behaviour
change is deliberately excluded so the guard stays focused on real wire preservation.
"""
from azure.ai.ml.entities import CodeConfiguration
from azure.ai.ml.entities._assets._artifacts._package.base_environment_source import BaseEnvironment
from azure.ai.ml.entities._assets._artifacts._package.inferencing_server import (
    AzureMLBatchInferencingServer,
    AzureMLOnlineInferencingServer,
)
from azure.ai.ml.entities._assets._artifacts._package.model_configuration import ModelConfiguration
from azure.ai.ml.entities._assets._artifacts._package.model_package import (
    ModelPackage,
    ModelPackageInput,
    PackageInputPathId,
)


def build_model_package_online():
    """ModelPackage with an AzureML online inferencing server, base env, model config and inputs."""
    return ModelPackage(
        target_environment="azureml:smoke-packaged-env:3",
        base_environment_source=BaseEnvironment(
            type="EnvironmentAsset",
            resource_id="azureml:smoke-base-env:1",
        ),
        inferencing_server=AzureMLOnlineInferencingServer(
            code_configuration=CodeConfiguration(code="azureml:smoke-code:1", scoring_script="score.py"),
        ),
        model_configuration=ModelConfiguration(mode="download", mount_path="/var/azureml-model"),
        inputs=[
            ModelPackageInput(
                type="uri_folder",
                path=PackageInputPathId(resource_id="azureml:smoke-model:1"),
                mode="download",
                mount_path="/var/inputs/model",
            ),
        ],
        environment_variables={"WORKER_COUNT": "2", "LOG_LEVEL": "INFO"},
    )


def build_model_package_batch_minimal():
    """Minimal ModelPackage with an AzureML batch inferencing server and no optional children."""
    return ModelPackage(
        target_environment="smoke-batch-packaged-env",
        inferencing_server=AzureMLBatchInferencingServer(),
    )


MODEL_PACKAGE_BUILDERS = {
    "model_package_online": build_model_package_online,
    "model_package_batch_minimal": build_model_package_batch_minimal,
}
