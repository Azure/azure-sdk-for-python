# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for online/batch DEPLOYMENT entities (smoke serialization suite).

Deployments serialize via a location-bound ``_to_rest_object(location)`` returning a rest deployment
model, so each builder returns a ``_RestAdapter`` exposing the suite's uniform no-arg
``_to_rest_object()`` contract (same pattern as ``_builders_endpoint.py``).

Deployments were the trickiest part of the client migration: pre-#47554 the online/batch deployment
envelope was a per-version msrest model while nested children (probes, scale settings) were already
``arm_ml_service`` hybrids -- a mixed tree the operations layer resolved at send time. That mixed tree
means the PRE-MIGRATION baseline cannot serialize a deployment offline at all (msrest ``.serialize()``
raises ``'ProbeSettings' has no _attribute_map``), so there is no baseline wire to pin against. The
migration unifies the whole tree on ``arm_ml_service``, so the branch now DOES serialize cleanly --
which is exactly what these builders assert via a serialization guard (``test_deployment_wire.py``).

Because no baseline golden is possible, these registries are named ``*_CASES`` (not ``*_BUILDERS``) so
the baseline capture in ``regenerate_expected_wire.py`` and the round-trip discovery do NOT pick them
up; the deployment test references them directly.
"""
from azure.ai.ml.entities import (
    BatchRetrySettings,
    CodeConfiguration,
    DefaultScaleSettings,
    ManagedOnlineDeployment,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    OnlineRequestSettings,
    ProbeSettings,
)

_LOCATION = "westus"


class _RestAdapter:
    """Expose a location-bound rest method as the suite's no-arg ``_to_rest_object()`` contract.

    :param entity: The deployment entity.
    :param location: The location string to pass to ``_to_rest_object``.
    """

    def __init__(self, entity, location=_LOCATION):
        self._entity = entity
        self._location = location

    def _to_rest_object(self):
        """Call the entity's location-taking rest method with the fixed location.

        :return: The rest object for the deployment.
        :rtype: Any
        """
        return self._entity._to_rest_object(location=self._location)


def build_managed_online_deployment():
    """ManagedOnlineDeployment with model, env, code, scale/request settings and probes."""
    deployment = ManagedOnlineDeployment(
        name="smoke-blue",
        endpoint_name="smoke-online-endpoint",
        description="smoke managed online deployment",
        model="azureml:smoke-model:1",
        environment="azureml:smoke-env:1",
        code_configuration=CodeConfiguration(code="azureml:smoke-code:1", scoring_script="score.py"),
        instance_type="Standard_DS2_v2",
        instance_count=2,
        app_insights_enabled=True,
        scale_settings=DefaultScaleSettings(),
        request_settings=OnlineRequestSettings(
            request_timeout_ms=3000,
            max_concurrent_requests_per_instance=1,
            max_queue_wait_ms=500,
        ),
        liveness_probe=ProbeSettings(
            failure_threshold=30,
            success_threshold=1,
            timeout=2,
            period=10,
            initial_delay=10,
        ),
        environment_variables={"WORKER_COUNT": "1"},
        tags={"tag1": "value1"},
    )
    return _RestAdapter(deployment)


def build_model_batch_deployment():
    """ModelBatchDeployment with model, env, compute and batch settings."""
    deployment = ModelBatchDeployment(
        name="smoke-batch-dep",
        endpoint_name="smoke-batch-endpoint",
        description="smoke model batch deployment",
        model="azureml:smoke-model:1",
        environment="azureml:smoke-env:1",
        compute="azureml:smoke-cluster",
        code_configuration=CodeConfiguration(code="azureml:smoke-code:1", scoring_script="score.py"),
        settings=ModelBatchDeploymentSettings(
            instance_count=2,
            max_concurrency_per_instance=1,
            mini_batch_size=10,
            output_action="append_row",
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
            error_threshold=-1,
            logging_level="info",
        ),
        tags={"tag1": "value1"},
    )
    return _RestAdapter(deployment)


ONLINE_DEPLOYMENT_CASES = {
    "managed_online_deployment": build_managed_online_deployment,
}

BATCH_DEPLOYMENT_CASES = {
    "model_batch_deployment": build_model_batch_deployment,
}
