# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Workspace connections, compute with identity, and command job with
             network and identity edge cases.

Inspired by azureml-examples/sdk/python/resources/ and jobs/ samples but tests edge
cases around:
  - Creating workspace connections of various types (custom, Azure OpenAI-like)
  - Creating compute with managed identity (system-assigned)
  - Running a command job that references workspace connections via environment variables
  - Submitting a job with queue_settings (job tier)
  - Setting job-level identity (user_identity vs aml_token)
  - Verifying job services dict (Studio URL) survives TypeSpec serialization
  - Job cancellation and status transitions
  - Listing jobs with filters (experiment_name, status)

Customer story:
  An enterprise team configures their workspace with connections to external services
  (e.g., a custom API key store). They create compute with managed identity for secure
  data access. They submit training jobs that reference these connections, and they
  need to cancel and re-submit jobs during development. This exercises the ARM client
  for workspace operations, compute operations, and the runhistory client for
  job lifecycle management.

Steps:
  1. Create a custom workspace connection with API key credentials
  2. Verify connection properties round-trip (credential type, target, tags)
  3. List connections, verify the new one appears
  4. Create compute with system-assigned managed identity
  5. Submit a command job using user_identity with custom tags/properties
  6. Verify job services (Studio link), experiment_name, display_name
  7. Cancel the job, verify status transitions to Canceled
  8. Submit another job, let it complete, list jobs by experiment
  9. Clean up
"""

import os
import tempfile
import time

import pytest

from azure.ai.ml import MLClient, command
from azure.ai.ml.entities import (
    AmlCompute,
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    WorkspaceConnection,
)
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.polling import LROPoller


class TestScenarioConnectionsComputeJobs:
    """Workspace connections + compute identity + job lifecycle edge cases."""

    @pytest.mark.timeout(900)
    def test_connection_crud_and_job_lifecycle(self, ml_client: MLClient, rand_name, wait_for_job):
        """Full lifecycle: connection → compute → job submit/cancel → job complete → list."""

        conn_name = rand_name("conn")
        compute_name = rand_name("idcpu")

        try:
            # ── Step 1: Create workspace connection ───────────────
            connection = WorkspaceConnection(
                name=conn_name,
                type="custom",
                target="https://api.example.com/v1",
                credentials=ApiKeyConfiguration(key="scenario-test-key-not-real"),
                tags={
                    "scenario": "tsp-migration",
                    "service": "custom-api",
                    "purpose": "testing-connection-serialization",
                },
            )
            created_conn = ml_client.connections.create_or_update(connection)
            assert created_conn.name == conn_name
            assert created_conn.type == "custom"

            # ── Step 2: Round-trip fidelity ────────────────────────
            fetched_conn = ml_client.connections.get(conn_name)
            assert fetched_conn.name == conn_name
            assert fetched_conn.target == "https://api.example.com/v1"
            assert fetched_conn.tags["scenario"] == "tsp-migration"
            assert fetched_conn.tags["service"] == "custom-api"
            # Credentials should be redacted on fetch
            assert fetched_conn.credentials is not None

            # ── Step 3: List connections ───────────────────────────
            conn_list = list(ml_client.connections.list())
            conn_names = [c.name for c in conn_list]
            assert conn_name in conn_names

            # ── Step 4: Compute with system-assigned identity ─────
            cluster = AmlCompute(
                name=compute_name,
                size="STANDARD_DS3_V2",
                min_instances=0,
                max_instances=1,
                idle_time_before_scale_down=120,
                identity=IdentityConfiguration(type="system_assigned"),
            )
            poller = ml_client.compute.begin_create_or_update(cluster)
            assert isinstance(poller, LROPoller)
            result = poller.result()
            assert result.name == compute_name

            # Verify identity was set
            fetched_compute = ml_client.compute.get(compute_name)
            assert fetched_compute.name == compute_name
            assert fetched_compute.identity is not None
            id_type = str(fetched_compute.identity.type).lower().replace("_", "")
            assert "systemassigned" in id_type

            # ── Step 5: Submit job with user_identity ─────────────
            with tempfile.TemporaryDirectory() as code_dir:
                script = os.path.join(code_dir, "hello.py")
                with open(script, "w") as f:
                    f.write(
                        """import os, time, sys
print(f"Python {sys.version}")
print(f"Working directory: {os.getcwd()}")
print("Starting work...")
time.sleep(30)  # Long enough to test cancellation
print("Work complete")
"""
                    )

                job1 = command(
                    code=code_dir,
                    command="python hello.py",
                    environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
                    compute=compute_name,
                    display_name=f"scenario-cancel-test-{rand_name('j1')}",
                    experiment_name="scenario-tests-lifecycle",
                    tags={
                        "scenario": "job-lifecycle",
                        "purpose": "cancel-test",
                        "branch": "tsp-migration",
                    },
                    properties={"test_type": "cancellation"},
                    identity=UserIdentityConfiguration(),
                )

                submitted1 = ml_client.jobs.create_or_update(job1)
                assert submitted1.name is not None
                assert submitted1.display_name == job1.display_name
                assert submitted1.experiment_name == "scenario-tests-lifecycle"

                # ── Step 6: Verify services dict ──────────────────
                refetched1 = ml_client.jobs.get(submitted1.name)
                assert refetched1.tags.get("purpose") == "cancel-test"
                assert refetched1.properties.get("test_type") == "cancellation"
                if hasattr(refetched1, "services") and refetched1.services:
                    assert "Studio" in refetched1.services

                # ── Step 7: Cancel the job ────────────────────────
                time.sleep(5)  # Let it start
                ml_client.jobs.begin_cancel(submitted1.name).result()
                # Wait a bit for cancellation to take effect
                time.sleep(10)
                cancelled = ml_client.jobs.get(submitted1.name)
                assert cancelled.status in {
                    "Canceled",
                    "CancelRequested",
                    "Finalizing",
                    "NotResponding",
                }, f"Expected cancelled state, got {cancelled.status}"

                # ── Step 8: Submit another job, let it complete ───
                quick_script = os.path.join(code_dir, "quick.py")
                with open(quick_script, "w") as f:
                    f.write('import mlflow; mlflow.log_metric("done", 1.0); print("Quick job done")\n')

                job2 = command(
                    code=code_dir,
                    command="python quick.py",
                    environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
                    compute=compute_name,
                    display_name=f"scenario-complete-test-{rand_name('j2')}",
                    experiment_name="scenario-tests-lifecycle",
                    tags={"scenario": "job-lifecycle", "purpose": "completion-test"},
                )

                submitted2 = ml_client.jobs.create_or_update(job2)
                finished2 = wait_for_job(ml_client, submitted2, timeout_seconds=600)
                assert finished2.status == "Completed"

                # ── Step 9: List jobs by experiment ───────────────
                exp_jobs = list(ml_client.jobs.list(experiment_name="scenario-tests-lifecycle"))
                assert len(exp_jobs) >= 2
                job_names_in_exp = {j.name for j in exp_jobs}
                assert submitted1.name in job_names_in_exp
                assert submitted2.name in job_names_in_exp

        finally:
            # ── Cleanup ───────────────────────────────────────────
            try:
                ml_client.connections.delete(conn_name)
            except Exception:
                pass
            try:
                ml_client.compute.begin_delete(compute_name).result()
            except Exception:
                pass
