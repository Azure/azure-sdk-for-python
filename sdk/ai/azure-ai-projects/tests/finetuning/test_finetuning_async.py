# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import os
import asyncio
from pathlib import Path
from test_base import (
    TestBase,
    servicePreparer,
    SFT_JOB_TYPE,
    DPO_JOB_TYPE,
    RFT_JOB_TYPE,
    STANDARD_TRAINING_TYPE,
    GLOBAL_STANDARD_TRAINING_TYPE,
)
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient as CognitiveServicesManagementClientAsync
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentProperties, DeploymentModel, Sku


@pytest.mark.skipif(
    condition=(not is_live_and_not_recording()),
    reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuningAsync(TestBase):

    async def _create_sft_finetuning_job_async(
        self, openai_client, train_file_id, validation_file_id, training_type, model_type
    ):
        return await openai_client.fine_tuning.jobs.create(
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

    async def _create_dpo_finetuning_job_async(
        self, openai_client, train_file_id, validation_file_id, training_type, model_type
    ):
        return await openai_client.fine_tuning.jobs.create(
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

    async def _create_rft_finetuning_job_async(
        self, openai_client, train_file_id, validation_file_id, training_type, model_type
    ):
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

        return await openai_client.fine_tuning.jobs.create(
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

    async def _upload_test_files_async(self, openai_client, job_type):
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with open(training_file_path, "rb") as f:
            train_file = await openai_client.files.create(file=f, purpose="fine-tune")
        train_processed_file = await openai_client.files.wait_for_processing(train_file.id)
        assert train_processed_file is not None
        assert train_processed_file.id is not None
        TestBase.assert_equal_or_not_none(train_processed_file.status, "processed")
        print(f"[_upload_test_files_async] Uploaded training file: {train_processed_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
        validation_processed_file = await openai_client.files.wait_for_processing(validation_file.id)
        assert validation_processed_file is not None
        assert validation_processed_file.id is not None
        TestBase.assert_equal_or_not_none(validation_processed_file.status, "processed")
        print(f"[_upload_test_files_async] Uploaded validation file: {validation_processed_file.id}")

        return train_processed_file, validation_processed_file

    async def _cleanup_test_file_async(self, openai_client, file_id):
        await openai_client.files.delete(file_id)
        print(f"[_cleanup_test_file_async] Deleted file: {file_id}")

    async def _test_cancel_job_helper_async(self, job_type, model_type, training_type, expected_method_type, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, job_type)

            if job_type == SFT_JOB_TYPE:
                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            elif job_type == DPO_JOB_TYPE:
                fine_tuning_job = await self._create_dpo_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            elif job_type == RFT_JOB_TYPE:
                fine_tuning_job = await self._create_rft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            else:
                raise ValueError(f"Unsupported job type: {job_type}")

            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Created job: {fine_tuning_job.id}")

            cancelled_job = await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Cancelled job: {cancelled_job.id}")

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
            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(
                f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Verified cancellation persisted for job: {retrieved_job.id}"
            )
            TestBase.validate_fine_tuning_job(
                retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
            )

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_sft_create_job_helper_async(self, model_type, training_type, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, SFT_JOB_TYPE)

            fine_tuning_job = await self._create_sft_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, training_type, model_type
            )
            print(f"[test_finetuning_sft_{model_type}_{training_type}] Created fine-tuning job: {fine_tuning_job.id}")

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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_sft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_dpo_create_job_helper_async(self, model_type, training_type, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, DPO_JOB_TYPE)

            fine_tuning_job = await self._create_dpo_finetuning_job_async(
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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_dpo_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_rft_create_job_helper_async(self, model_type, training_type, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, RFT_JOB_TYPE)

            fine_tuning_job = await self._create_rft_finetuning_job_async(
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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_rft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    def _extract_account_name_from_endpoint(self, project_endpoint, test_prefix):
        endpoint_clean = project_endpoint.replace("https://", "").replace("http://", "")
        if ".services.ai.azure.com" not in endpoint_clean:
            raise ValueError(
                f"Invalid project endpoint format: {project_endpoint} - expected format with .services.ai.azure.com"
            )
        return endpoint_clean.split(".services.ai.azure.com")[0]

    async def _test_deploy_and_infer_helper_async(
        self, completed_job_id_env_var, deployment_format, deployment_capacity, test_prefix, inference_content, **kwargs
    ):
        completed_job_id = os.getenv(completed_job_id_env_var)

        if not completed_job_id:
            pytest.skip(
                f"{completed_job_id_env_var} environment variable not set - skipping {test_prefix} deploy and infer test"
            )

        subscription_id = os.getenv("AZURE_AI_PROJECTS_TESTS_AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_AI_PROJECTS_TESTS_AZURE_RESOURCE_GROUP")
        project_endpoint = os.getenv("AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT")

        if not all([subscription_id, resource_group, project_endpoint]):
            pytest.skip(
                f"Missing required environment variables for deployment (AZURE_AI_PROJECTS_TESTS_AZURE_SUBSCRIPTION_ID, AZURE_AI_PROJECTS_TESTS_AZURE_RESOURCE_GROUP, AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT) - skipping {test_prefix} deploy and infer test"
            )

        account_name = self._extract_account_name_from_endpoint(project_endpoint, test_prefix)
        print(f"[{test_prefix}] Account name: {account_name}")

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            print(f"[{test_prefix}] Testing deployment and inference for job: {completed_job_id}")

            job = await openai_client.fine_tuning.jobs.retrieve(completed_job_id)
            print(f"[{test_prefix}] Job status: {job.status}")

            fine_tuned_model_name = job.fine_tuned_model
            deployment_name = f"test-{completed_job_id[-8:]}"

            print(f"[{test_prefix}] Fine-tuned model: {fine_tuned_model_name}, Deployment name: {deployment_name}")

            credential = self.get_credential(CognitiveServicesManagementClientAsync, is_async=True)

            async with CognitiveServicesManagementClientAsync(
                credential=credential, subscription_id=subscription_id
            ) as cogsvc_client:

                deployment_model = DeploymentModel(format=deployment_format, name=fine_tuned_model_name, version="1")
                deployment_properties = DeploymentProperties(model=deployment_model)
                deployment_sku = Sku(name="GlobalStandard", capacity=deployment_capacity)
                deployment_config = Deployment(properties=deployment_properties, sku=deployment_sku)

                print(f"[{test_prefix}] Starting deployment...")
                deployment_operation = await cogsvc_client.deployments.begin_create_or_update(
                    resource_group_name=resource_group,
                    account_name=account_name,
                    deployment_name=deployment_name,
                    deployment=deployment_config,
                )

                while deployment_operation.status() not in ["Succeeded", "Failed"]:
                    await asyncio.sleep(30)
                    print(f"[{test_prefix}] Deployment status: {deployment_operation.status()}")

                print(f"[{test_prefix}] Deployment completed successfully")

                print(f"[{test_prefix}] Testing inference on deployment: {deployment_name}")
                await asyncio.sleep(120)  # Wait for deployment to be fully ready

                response = await openai_client.responses.create(
                    model=deployment_name, input=[{"role": "user", "content": inference_content}]
                )

                assert response is not None, "Response should not be None"
                assert hasattr(response, "output_text"), "Response should have output_text attribute"
                assert response.output_text is not None, "Response output_text should not be None"

                print(f"[{test_prefix}] Successfully validated inference response")

                print(f"[{test_prefix}] Cleaning up deployment: {deployment_name}")
                await cogsvc_client.deployments.begin_delete(
                    resource_group_name=resource_group, account_name=account_name, deployment_name=deployment_name
                )
                print(f"[{test_prefix}] Deployment cleanup initiated")
                print(
                    f"[{test_prefix}] Successfully completed deployment and inference test for job: {completed_job_id}"
                )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_openai_standard_async(self, **kwargs):
        await self._test_sft_create_job_helper_async("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        await self._test_sft_create_job_helper_async("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_oss_globalstandard_async(self, **kwargs):
        await self._test_sft_create_job_helper_async("oss", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_openai_standard_async(self, **kwargs):
        await self._test_dpo_create_job_helper_async("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        await self._test_dpo_create_job_helper_async("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_openai_standard_async(self, **kwargs):
        await self._test_rft_create_job_helper_async("openai", STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        await self._test_rft_create_job_helper_async("openai", GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_sft_job_async(self, **kwargs):
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, SFT_JOB_TYPE)

            fine_tuning_job = await self._create_sft_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
            )
            print(f"[test_finetuning_retrieve_sft] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_sft] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_dpo_job_async(self, **kwargs):
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, DPO_JOB_TYPE)

            fine_tuning_job = await self._create_dpo_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
            )
            print(f"[test_finetuning_retrieve_dpo] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_dpo] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_rft_job_async(self, **kwargs):
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, RFT_JOB_TYPE)

            fine_tuning_job = await self._create_rft_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
            )
            print(f"[test_finetuning_retrieve_rft] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
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

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_rft] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_jobs_async(self, **kwargs):
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            jobs_list_async = openai_client.fine_tuning.jobs.list()
            jobs_list = []
            async for job in jobs_list_async:
                jobs_list.append(job)
            print(f"[test_finetuning_list] Listed {len(jobs_list)} jobs")

            assert isinstance(jobs_list, list), "Jobs list should be a list"

            for job in jobs_list:
                assert job.id is not None, "Job should have an ID"
                assert job.created_at is not None, "Job should have a creation timestamp"
                assert job.status is not None, "Job should have a status"
                print(f"[test_finetuning_list] Validated job {job.id} with status {job.status}")
            print(f"[test_finetuning_list] Successfully validated list functionality with {len(jobs_list)} jobs")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_cancel_job_openai_standard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(SFT_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_cancel_job_openai_globalstandard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(
            SFT_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_cancel_job_oss_globalstandard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(
            SFT_JOB_TYPE, "oss", GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_cancel_job_openai_standard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(DPO_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_cancel_job_openai_globalstandard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(DPO_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_cancel_job_openai_standard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(
            RFT_JOB_TYPE, "openai", STANDARD_TRAINING_TYPE, "reinforcement", **kwargs
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_cancel_job_openai_globalstandard_async(self, **kwargs):
        await self._test_cancel_job_helper_async(
            RFT_JOB_TYPE, "openai", GLOBAL_STANDARD_TRAINING_TYPE, "reinforcement", **kwargs
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_events_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, SFT_JOB_TYPE)

            fine_tuning_job = await self._create_sft_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, STANDARD_TRAINING_TYPE, "openai"
            )
            print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

            TestBase.validate_fine_tuning_job(fine_tuning_job)
            TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

            events_list_async = openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id)
            events_list = []
            async for event in events_list_async:
                events_list.append(event)
            print(f"[test_finetuning_sft] Listed {len(events_list)} events for job: {fine_tuning_job.id}")

            assert len(events_list) > 0, "Fine-tuning job should have at least one event"

            for event in events_list:
                assert event.id is not None, "Event should have an ID"
                assert event.object is not None, "Event should have an object type"
                assert event.created_at is not None, "Event should have a creation timestamp"
                assert event.level is not None, "Event should have a level"
                assert event.message is not None, "Event should have a message"
                assert event.type is not None, "Event should have a type"
            print(f"[test_finetuning_sft] Successfully validated {len(events_list)} events")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_pause_job_async(self, **kwargs):
        running_job_id = os.getenv("AZURE_AI_PROJECTS_TESTS_RUNNING_FINE_TUNING_JOB_ID")

        if not running_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_RUNNING_FINE_TUNING_JOB_ID environment variable not set - skipping pause test"
            )

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            print(f"[test_finetuning_pause] Testing pause functionality on job: {running_job_id}")

            job = await openai_client.fine_tuning.jobs.retrieve(running_job_id)
            print(f"[test_finetuning_pause] Job status before pause: {job.status}")

            if job.status != "running":
                pytest.skip(
                    f"Job {running_job_id} is in status '{job.status}' - only testing pause on 'running' status - skipping test"
                )

            paused_job = await openai_client.fine_tuning.jobs.pause(running_job_id)
            print(f"[test_finetuning_pause] Paused job: {paused_job.id}")

            TestBase.validate_fine_tuning_job(paused_job, expected_job_id=running_job_id)
            TestBase.assert_equal_or_not_none(paused_job.status, "paused")
            print(f"[test_finetuning_pause] Job status after pause: {paused_job.status}")

            print(f"[test_finetuning_pause] Successfully paused and verified job: {running_job_id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_resume_job_async(self, **kwargs):
        paused_job_id = os.getenv("AZURE_AI_PROJECTS_TESTS_PAUSED_FINE_TUNING_JOB_ID")

        if not paused_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_PAUSED_FINE_TUNING_JOB_ID environment variable not set - skipping resume test"
            )

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            print(f"[test_finetuning_resume] Testing resume functionality on job: {paused_job_id}")

            job = await openai_client.fine_tuning.jobs.retrieve(paused_job_id)
            print(f"[test_finetuning_resume] Job status before resume: {job.status}")

            if job.status != "paused":
                pytest.skip(
                    f"Job {paused_job_id} is in status '{job.status}' - only testing resume on 'paused' status - skipping test"
                )

            resumed_job = await openai_client.fine_tuning.jobs.resume(paused_job_id)
            print(f"[test_finetuning_resume] Resumed job: {resumed_job.id}")

            TestBase.validate_fine_tuning_job(resumed_job, expected_job_id=paused_job_id)
            print(f"[test_finetuning_resume] Job status after resume: {resumed_job.status}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_checkpoints_async(self, **kwargs):
        completed_job_id = os.getenv("AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_SFT_FINE_TUNING_JOB_ID")

        if not completed_job_id:
            pytest.skip(
                "AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_SFT_FINE_TUNING_JOB_ID environment variable not set - skipping checkpoints test"
            )

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            print(
                f"[test_finetuning_list_checkpoints] Testing list checkpoints functionality on job: {completed_job_id}"
            )

            job = await openai_client.fine_tuning.jobs.retrieve(completed_job_id)
            print(f"[test_finetuning_list_checkpoints] Job status: {job.status}")

            checkpoints_list_async = openai_client.fine_tuning.jobs.checkpoints.list(completed_job_id)
            checkpoints_list = [checkpoint async for checkpoint in checkpoints_list_async]
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
    @recorded_by_proxy_async
    async def test_finetuning_deploy_and_infer_oai_model_sft_job_async(self, **kwargs):
        await self._test_deploy_and_infer_helper_async(
            "AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_SFT_FINE_TUNING_JOB_ID",
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_sft_job",
            "Who invented the telephone?",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_deploy_and_infer_oai_model_rft_job_async(self, **kwargs):
        await self._test_deploy_and_infer_helper_async(
            "AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_RFT_FINE_TUNING_JOB_ID",
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_rft_job",
            "Target: 85 Numbers: [20, 4, 15, 10]. Find a mathematical expression using all numbers exactly once to reach the target.",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_deploy_and_infer_oai_model_dpo_job_async(self, **kwargs):
        await self._test_deploy_and_infer_helper_async(
            "AZURE_AI_PROJECTS_TESTS_COMPLETED_OAI_MODEL_DPO_FINE_TUNING_JOB_ID",
            "OpenAI",
            50,
            "test_finetuning_deploy_and_infer_oai_model_dpo_job",
            "What is the largest desert in the world?",
            **kwargs,
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_deploy_and_infer_oss_model_sft_job_async(self, **kwargs):
        await self._test_deploy_and_infer_helper_async(
            "AZURE_AI_PROJECTS_TESTS_COMPLETED_OSS_MODEL_SFT_FINE_TUNING_JOB_ID",
            "Mistral AI",
            50,
            "test_finetuning_deploy_and_infer_oss_model_sft_job",
            "Who invented the telephone?",
            **kwargs,
        )
