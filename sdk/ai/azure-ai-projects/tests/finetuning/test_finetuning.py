# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import os
import time
from pathlib import Path
from test_base import (
    TestBase,
    servicePreparer,
    SFT_JOB_TYPE,
    DPO_JOB_TYPE,
    RFT_JOB_TYPE,
    STANDARD_TRAINING_TYPE,
    GLOBAL_STANDARD_TRAINING_TYPE,
    DEVELOPER_TIER_TRAINING_TYPE,
)
from devtools_testutils import (
    recorded_by_proxy,
    RecordedTransport,
    is_live
)
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentProperties, DeploymentModel, Sku


class TestFineTuning(TestBase):

    def _create_sft_finetuning_job(self, openai_client, train_file_id, validation_file_id, training_type, model_type):
        return openai_client.fine_tuning.jobs.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model=self.test_finetuning_params["sft"][model_type]["model_name"],
            method={
                "type": "supervised",
                "supervised": {
                    "hyperparameters": {
                        "n_epochs": self.test_finetuning_params["n_epochs"],
                        "batch_size": self.test_finetuning_params["batch_size"],
                        "learning_rate_multiplier": self.test_finetuning_params["learning_rate_multiplier"],
                    }
                },
            },
            extra_body={"trainingType": training_type},
        )

    def _create_dpo_finetuning_job(self, openai_client, train_file_id, validation_file_id, training_type, model_type):
        return openai_client.fine_tuning.jobs.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model=self.test_finetuning_params["dpo"][model_type]["model_name"],
            method={
                "type": "dpo",
                "dpo": {
                    "hyperparameters": {
                        "n_epochs": self.test_finetuning_params["n_epochs"],
                        "batch_size": self.test_finetuning_params["batch_size"],
                        "learning_rate_multiplier": self.test_finetuning_params["learning_rate_multiplier"],
                    }
                },
            },
            extra_body={"trainingType": training_type},
        )

    def _create_rft_finetuning_job(self, openai_client, train_file_id, validation_file_id, training_type, model_type):
        grader = {
            "name": "Response Quality Grader",
            "type": "score_model",
            "model": "o3-mini",
            "input": [
                {
                    "role": "user",
                    "content": "Evaluate the model's response based on correctness and quality. Rate from 0 to 10.",
                }
            ],
            "range": [0.0, 10.0],
        }

        return openai_client.fine_tuning.jobs.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model=self.test_finetuning_params["rft"][model_type]["model_name"],
            method={
                "type": "reinforcement",
                "reinforcement": {
                    "grader": grader,
                    "hyperparameters": {
                        "n_epochs": self.test_finetuning_params["n_epochs"],
                        "batch_size": self.test_finetuning_params["batch_size"],
                        "learning_rate_multiplier": self.test_finetuning_params["learning_rate_multiplier"],
                        "eval_interval": 5,
                        "eval_samples": 2,
                        "reasoning_effort": "medium",
                    },
                },
            },
            extra_body={"trainingType": training_type},
        )

    def _upload_test_files(self, openai_client, job_type):
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with self.open_with_lf(str(training_file_path), "rb") as f:
            train_file = openai_client.files.create(file=f, purpose="fine-tune")
        train_processed_file = openai_client.files.wait_for_processing(train_file.id)
        assert train_processed_file is not None
        assert train_processed_file.id is not None
        TestBase.assert_equal_or_not_none(train_processed_file.status, "processed")
        print(f"[_upload_test_files] Uploaded training file: {train_processed_file.id}")

        with self.open_with_lf(str(validation_file_path), "rb") as f:
            validation_file = openai_client.files.create(file=f, purpose="fine-tune")
        validation_processed_file = openai_client.files.wait_for_processing(validation_file.id)
        assert validation_processed_file is not None
        assert validation_processed_file.id is not None
        TestBase.assert_equal_or_not_none(validation_processed_file.status, "processed")
        print(f"[_upload_test_files] Uploaded validation file: {validation_processed_file.id}")

        return train_processed_file, validation_processed_file

    def _cleanup_test_file(self, openai_client, file_id):
        openai_client.files.delete(file_id)
        print(f"[_cleanup_test_file] Deleted file: {file_id}")

    def _test_cancel_job_helper(self, job_type, model_type, training_type, expected_method_type, **kwargs):

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, job_type)

                if job_type == SFT_JOB_TYPE:
                    fine_tuning_job = self._create_sft_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                elif job_type == DPO_JOB_TYPE:
                    fine_tuning_job = self._create_dpo_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                elif job_type == RFT_JOB_TYPE:
                    fine_tuning_job = self._create_rft_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                else:
                    raise ValueError(f"Unsupported job type: {job_type}")

                print(
                    f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Created job: {fine_tuning_job.id}"
                )

                cancelled_job = openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(
                    f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Cancelled job: {cancelled_job.id}"
                )

                # Validate the cancelled job
                TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")
                TestBase.assert_equal_or_not_none(cancelled_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(cancelled_job.validation_file, validation_file.id)

                # Validate method type
                assert cancelled_job.method is not None, f"Method should not be None for {job_type} job"
                TestBase.assert_equal_or_not_none(cancelled_job.method.type, expected_method_type)
                print(
                    f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Method validation passed - type: {cancelled_job.method.type}"
                )

                # Verify cancellation persisted by retrieving the job
                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(
                    f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Verified cancellation persisted for job: {retrieved_job.id}"
                )
                TestBase.validate_fine_tuning_job(
                    retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
                )

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _test_sft_create_job_helper(self, model_type, training_type, **kwargs):

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
                print(
                    f"[test_finetuning_sft_{model_type}_{training_type}] Created fine-tuning job: {fine_tuning_job.id}"
                )

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(
                    f"[test_finetuning_sft_{model_type}_{training_type}] SFT method validation passed - type: {fine_tuning_job.method.type}"
                )

                # For OSS models, validate the specific model name
                if model_type == "oss":
                    TestBase.validate_fine_tuning_job(
                        fine_tuning_job, expected_model=self.test_finetuning_params["sft"]["oss"]["model_name"]
                    )

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _test_dpo_create_job_helper(self, model_type, training_type, **kwargs):

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, DPO_JOB_TYPE)

                fine_tuning_job = self._create_dpo_finetuning_job(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
                print(
                    f"[test_finetuning_dpo_{model_type}_{training_type}] Created DPO fine-tuning job: {fine_tuning_job.id}"
                )
                print(fine_tuning_job)

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "dpo")

                print(
                    f"[test_finetuning_dpo_{model_type}_{training_type}] DPO method validation passed - type: {fine_tuning_job.method.type}"
                )

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_dpo_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _test_rft_create_job_helper(self, model_type, training_type, **kwargs):

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, RFT_JOB_TYPE)

                fine_tuning_job = self._create_rft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
                print(
                    f"[test_finetuning_rft_{model_type}_{training_type}] Created RFT fine-tuning job: {fine_tuning_job.id}"
                )

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "reinforcement")

                print(
                    f"[test_finetuning_rft_{model_type}_{training_type}] RFT method validation passed - type: {fine_tuning_job.method.type}"
                )

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_rft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _extract_account_name_from_endpoint(self, project_endpoint, test_prefix):
        endpoint_clean = project_endpoint.replace("https://", "").replace("http://", "")
        if ".services.ai.azure.com" not in endpoint_clean:
            raise ValueError(
                f"Invalid project endpoint format: {project_endpoint} - expected format with .services.ai.azure.com"
            )
        return endpoint_clean.split(".services.ai.azure.com")[0]

    def _test_deploy_and_infer_helper(
        self, completed_job_id, deployment_format, deployment_capacity, test_prefix, inference_content, **kwargs
    ):
        if not completed_job_id:
            pytest.skip(f"completed_job_id parameter not set - skipping {test_prefix} deploy and infer test")

        subscription_id = kwargs.get("azure_ai_projects_tests_azure_subscription_id")
        resource_group = kwargs.get("azure_ai_projects_tests_azure_resource_group")
        project_endpoint = kwargs.get("azure_ai_projects_tests_project_endpoint")

        if not all([subscription_id, resource_group, project_endpoint]):
            pytest.skip(
                f"Missing required environment variables for deployment (AZURE_AI_PROJECTS_TESTS_AZURE_SUBSCRIPTION_ID, AZURE_AI_PROJECTS_TESTS_AZURE_RESOURCE_GROUP, AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT) - skipping {test_prefix} deploy and infer test"
            )

        account_name = self._extract_account_name_from_endpoint(project_endpoint, test_prefix)
        print(f"[{test_prefix}] Account name: {account_name}")

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                print(f"[{test_prefix}] Testing deployment and inference for job: {completed_job_id}")

                job = openai_client.fine_tuning.jobs.retrieve(completed_job_id)
                print(f"[{test_prefix}] Job status: {job.status}")

                fine_tuned_model_name = job.fine_tuned_model
                deployment_name = f"test-{completed_job_id[-8:]}"

                print(f"[{test_prefix}] Fine-tuned model: {fine_tuned_model_name}, Deployment name: {deployment_name}")

                credential = self.get_credential(CognitiveServicesManagementClient, is_async=False)

                with CognitiveServicesManagementClient(
                    credential=credential, subscription_id=subscription_id
                ) as cogsvc_client:

                    deployment_model = DeploymentModel(
                        format=deployment_format, name=fine_tuned_model_name, version="1"
                    )
                    deployment_properties = DeploymentProperties(model=deployment_model)
                    deployment_sku = Sku(name="GlobalStandard", capacity=deployment_capacity)
                    deployment_config = Deployment(properties=deployment_properties, sku=deployment_sku)

                    print(f"[{test_prefix}] Starting deployment...")
                    deployment_operation = cogsvc_client.deployments.begin_create_or_update(
                        resource_group_name=resource_group,
                        account_name=account_name,
                        deployment_name=deployment_name,
                        deployment=deployment_config,
                    )

                    while deployment_operation.status() not in ["Succeeded", "Failed"]:
                        time.sleep(30)
                        print(f"[{test_prefix}] Deployment status: {deployment_operation.status()}")

                    print(f"[{test_prefix}] Deployment completed successfully")
                    if is_live():
                        print(f"[{test_prefix}] Waiting for 10 minutes for deployment to be fully ready.")
                        time.sleep(600)
                    print(f"[{test_prefix}] Testing inference on deployment: {deployment_name}")

                    response = openai_client.responses.create(
                        model=deployment_name, input=[{"role": "user", "content": inference_content}]
                    )

                    assert response is not None, "Response should not be None"
                    assert hasattr(response, "output_text"), "Response should have output_text attribute"
                    assert response.output_text is not None, "Response output_text should not be None"

                    print(f"[{test_prefix}] Successfully validated inference response")

                    print(f"[{test_prefix}] Cleaning up deployment: {deployment_name}")
                    cogsvc_client.deployments.begin_delete(
                        resource_group_name=resource_group, account_name=account_name, deployment_name=deployment_name
                    )
                    print(f"[{test_prefix}] Deployment cleanup initiated")
                    print(
                        f"[{test_prefix}] Successfully completed deployment and inference test for job: {completed_job_id}"
                    )

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_finetuning_create_job_openai_standard(self, **kwargs):
        self._test_sft_create_job_helper("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_finetuning_create_job_openai_developer(self, **kwargs):
        self._test_sft_create_job_helper("openai", DEVELOPER_TIER_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_finetuning_create_job_openai_globalstandard(self, **kwargs):
        self._test_sft_create_job_helper("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_finetuning_create_job_oss_globalstandard(self, **kwargs):
        self._test_sft_create_job_helper("oss", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_finetuning_create_job_openai_standard(self, **kwargs):
        self._test_dpo_create_job_helper("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_finetuning_create_job_openai__developer(self, **kwargs):
        self._test_dpo_create_job_helper("openai", DEVELOPER_TIER_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_finetuning_create_job_openai_globalstandard(self, **kwargs):
        self._test_dpo_create_job_helper("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_finetuning_create_job_openai_standard(self, **kwargs):
        self._test_rft_create_job_helper("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_finetuning_create_job_openai_globalstandard(self, **kwargs):
        self._test_rft_create_job_helper("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_finetuning_create_job_openai_developer(self, **kwargs):
        self._test_rft_create_job_helper("openai", DEVELOPER_TIER_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_retrieve_sft_job(self, **kwargs):
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
                )
                print(f"[test_finetuning_retrieve_sft] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_sft] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "supervised")
                assert (
                    self.test_finetuning_params["sft"]["openai"]["model_name"] in retrieved_job.model
                ), f"Expected model name {self.test_finetuning_params['sft']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_retrieve_dpo_job(self, **kwargs):
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, DPO_JOB_TYPE)

                fine_tuning_job = self._create_dpo_finetuning_job(
                    openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
                )
                print(f"[test_finetuning_retrieve_dpo] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_dpo] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "dpo")
                assert (
                    self.test_finetuning_params["dpo"]["openai"]["model_name"] in retrieved_job.model
                ), f"Expected model name {self.test_finetuning_params['dpo']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_dpo] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_retrieve_rft_job(self, **kwargs):
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, RFT_JOB_TYPE)

                fine_tuning_job = self._create_rft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
                )
                print(f"[test_finetuning_retrieve_rft] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_rft] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "reinforcement")
                assert (
                    self.test_finetuning_params["rft"]["openai"]["model_name"] in retrieved_job.model
                ), f"Expected model name {self.test_finetuning_params['rft']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_rft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_list_jobs(self, **kwargs):
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                jobs_list = list(openai_client.fine_tuning.jobs.list())
                print(f"[test_finetuning_list] Listed {len(jobs_list)} jobs")

                assert isinstance(jobs_list, list), "Jobs list should be a list"

                for job in jobs_list:
                    assert job.id is not None, "Job should have an ID"
                    assert job.created_at is not None, "Job should have a creation timestamp"
                    assert job.status is not None, "Job should have a status"
                    print(f"[test_finetuning_list] Validated job {job.id} with status {job.status}")
                print(f"[test_finetuning_list] Successfully validated list functionality with {len(jobs_list)} jobs")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_cancel_job_openai_standard(self, **kwargs):
        self._test_cancel_job_helper(SFT_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_cancel_job_openai_globalstandard(self, **kwargs):
        self._test_cancel_job_helper(SFT_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_cancel_job_openai_developer(self, **kwargs):
        self._test_cancel_job_helper(SFT_JOB_TYPE, "openai", DEVELOPER_TIER_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sft_cancel_job_oss_globalstandard(self, **kwargs):
        self._test_cancel_job_helper(SFT_JOB_TYPE, "oss", GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_cancel_job_openai_standard(self, **kwargs):
        self._test_cancel_job_helper(DPO_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_cancel_job_openai_globalstandard(self, **kwargs):
        self._test_cancel_job_helper(DPO_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_dpo_cancel_job_openai_developer(self, **kwargs):
        self._test_cancel_job_helper(DPO_JOB_TYPE, "openai", DEVELOPER_TIER_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_cancel_job_openai_standard(self, **kwargs):
        self._test_cancel_job_helper(RFT_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_cancel_job_openai_globalstandard(self, **kwargs):
        self._test_cancel_job_helper(RFT_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_rft_cancel_job_openai_developer(self, **kwargs):
        self._test_cancel_job_helper(RFT_JOB_TYPE, "openai", DEVELOPER_TIER_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_list_events(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
                )
                print(f"[test_finetuning_list_events] Created job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_list_events] Cancelled job: {fine_tuning_job.id}")

                events_list = list(openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id))
                print(f"[test_finetuning_list_events] Listed {len(events_list)} events for job: {fine_tuning_job.id}")

                assert len(events_list) > 0, "Fine-tuning job should have at least one event"

                for event in events_list:
                    assert event.id is not None, "Event should have an ID"
                    assert event.object is not None, "Event should have an object type"
                    assert event.created_at is not None, "Event should have a creation timestamp"
                    assert event.level is not None, "Event should have a level"
                    assert event.message is not None, "Event should have a message"
                    assert event.type is not None, "Event should have a type"
                print(f"[test_finetuning_list_events] Successfully validated {len(events_list)} events")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_pause_job(self, **kwargs):
        running_job_id = kwargs.get("azure_ai_projects_tests_running_fine_tuning_job_id")

        if not running_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_RUNNING_FINE_TUNING_JOB_ID environment variable not set - skipping pause test"
            )

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                print(f"[test_finetuning_pause_job] Testing pause functionality on job: {running_job_id}")

                job = openai_client.fine_tuning.jobs.retrieve(running_job_id)
                print(f"[test_finetuning_pause_job] Job status before pause: {job.status}")

                if job.status != "running":
                    pytest.skip(
                        f"Job {running_job_id} is in status '{job.status}' - only testing pause on 'running' status - skipping test"
                    )

                paused_job = openai_client.fine_tuning.jobs.pause(running_job_id)
                print(f"[test_finetuning_pause_job] Paused job: {paused_job.id}")

                TestBase.validate_fine_tuning_job(paused_job, expected_job_id=running_job_id)
                TestBase.assert_equal_or_not_none(paused_job.status, "pausing")
                print(f"[test_finetuning_pause_job] Job status after pause: {paused_job.status}")

                print(f"[test_finetuning_pause_job] Successfully paused and verified job: {running_job_id}")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_resume_job(self, **kwargs):
        paused_job_id = kwargs.get("azure_ai_projects_tests_paused_fine_tuning_job_id")

        if not paused_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_PAUSED_FINE_TUNING_JOB_ID environment variable not set - skipping resume test"
            )

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                print(f"[test_finetuning_resume_job] Testing resume functionality on job: {paused_job_id}")

                job = openai_client.fine_tuning.jobs.retrieve(paused_job_id)
                print(f"[test_finetuning_resume_job] Job status before resume: {job.status}")

                if job.status != "paused":
                    pytest.skip(
                        f"Job {paused_job_id} is in status '{job.status}' - only testing resume on 'paused' status - skipping test"
                    )

                resumed_job = openai_client.fine_tuning.jobs.resume(paused_job_id)
                print(f"[test_finetuning_resume_job] Resumed job: {resumed_job.id}")

                TestBase.validate_fine_tuning_job(resumed_job, expected_job_id=paused_job_id)
                TestBase.assert_equal_or_not_none(resumed_job.status, "resuming")
                print(f"[test_finetuning_resume_job] Job status after resume: {resumed_job.status}")
                print(f"[test_finetuning_resume_job] Successfully resumed and verified job: {paused_job_id}")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_list_checkpoints(self, **kwargs):
        completed_job_id = kwargs.get("azure_ai_projects_tests_completed_oai_model_sft_fine_tuning_job_id")

        if not completed_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_SFT_FINE_TUNING_JOB_ID environment variable not set - skipping checkpoints test"
            )

        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                print(
                    f"[test_finetuning_list_checkpoints] Testing list checkpoints functionality on job: {completed_job_id}"
                )

                job = openai_client.fine_tuning.jobs.retrieve(completed_job_id)
                print(f"[test_finetuning_list_checkpoints] Job status: {job.status}")

                checkpoints_list = list(openai_client.fine_tuning.jobs.checkpoints.list(completed_job_id))
                print(
                    f"[test_finetuning_list_checkpoints] Listed {len(checkpoints_list)} checkpoints for job: {completed_job_id}"
                )

                for checkpoint in checkpoints_list:
                    assert checkpoint.id is not None, "Checkpoint should have an ID"
                    assert checkpoint.created_at is not None, "Checkpoint should have a creation timestamp"
                    assert (
                        checkpoint.fine_tuning_job_id == completed_job_id
                    ), f"Checkpoint should belong to job {completed_job_id}"
                    assert checkpoint.step_number is not None, "Checkpoint should have a step number"
                    print(
                        f"[test_finetuning_list_checkpoints] Validated checkpoint {checkpoint.id} at step {checkpoint.step_number}"
                    )

                print(
                    f"[test_finetuning_list_checkpoints] Successfully validated {len(checkpoints_list)} checkpoints for job: {completed_job_id}"
                )

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_deploy_and_infer_oai_model_sft_job(self, **kwargs):
        completed_job_id = kwargs.get("azure_ai_projects_tests_completed_oai_model_sft_fine_tuning_job_id")
        self._test_deploy_and_infer_helper(
            completed_job_id,
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_sft_job",
            "Who invented the telephone?",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_deploy_and_infer_oai_model_rft_job(self, **kwargs):
        completed_job_id = kwargs.get("azure_ai_projects_tests_completed_oai_model_rft_fine_tuning_job_id")
        self._test_deploy_and_infer_helper(
            completed_job_id,
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_rft_job",
            "Target: 85 Numbers: [20, 4, 15, 10]. Find a mathematical expression using all numbers exactly once to reach the target.",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_deploy_and_infer_oai_model_dpo_job(self, **kwargs):
        completed_job_id = kwargs.get("azure_ai_projects_tests_completed_oai_model_dpo_fine_tuning_job_id")
        self._test_deploy_and_infer_helper(
            completed_job_id,
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_dpo_job",
            "What is the largest desert in the world?",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_finetuning_deploy_and_infer_oss_model_sft_job(self, **kwargs):
        completed_job_id = kwargs.get("azure_ai_projects_tests_completed_oss_model_sft_fine_tuning_job_id")
        self._test_deploy_and_infer_helper(
            completed_job_id,
            "Mistral AI",
            50,
            "test_finetuning_deploy_and_infer_oss_model_sft_job",
            "Who invented the telephone?",
            **kwargs,
        )
