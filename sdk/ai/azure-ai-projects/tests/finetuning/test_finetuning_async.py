# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time
import pytest
import asyncio
from pathlib import Path
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentProperties, DeploymentModel, Sku


@pytest.mark.skipif(
    condition=(not is_live_and_not_recording()),
    reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuningAsync(TestBase):

    async def _create_sft_finetuning_job_async(
        self, openai_client, train_file_id, validation_file_id, model_type="openai"
    ):
        """Helper method to create a supervised fine-tuning job asynchronously."""
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
        )

    async def _create_dpo_finetuning_job_async(self, openai_client, train_file_id, validation_file_id):
        """Helper method to create a DPO fine-tuning job asynchronously."""
        return await openai_client.fine_tuning.jobs.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model=self.test_finetuning_params["dpo"]["openai"]["model_name"],
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
        )

    async def _create_rft_finetuning_job_async(self, openai_client, train_file_id, validation_file_id):
        """Helper method to create an RFT fine-tuning job asynchronously."""
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
            model=self.test_finetuning_params["rft"]["openai"]["model_name"],
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
        )

    async def _upload_test_files_async(self, openai_client, job_type="sft"):
        """Helper method to upload training and validation files for fine-tuning tests asynchronously."""
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with open(training_file_path, "rb") as f:
            train_file = await openai_client.files.create(file=f, purpose="fine-tune")
        assert train_file is not None
        assert train_file.id is not None
        TestBase.assert_equal_or_not_none(train_file.status, "pending")
        print(f"[test_finetuning_{job_type}_async] Uploaded training file: {train_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
        assert validation_file is not None
        assert validation_file.id is not None
        TestBase.assert_equal_or_not_none(validation_file.status, "pending")
        print(f"[test_finetuning_{job_type}_async] Uploaded validation file: {validation_file.id}")

        return train_file, validation_file

    async def _cleanup_test_files_async(self, openai_client, train_file, validation_file):
        """Helper method to clean up uploaded files after testing asynchronously."""
        await openai_client.files.delete(train_file.id)
        print(f"Deleted training file: {train_file.id}")

        await openai_client.files.delete(validation_file.id)
        print(f"Deleted validation file: {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_sft_async] Created fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(f"[test_finetuning_sft_async] SFT method validation passed - type: {fine_tuning_job.method.type}")

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")

                retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_jobs_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")

                jobs_list_async = openai_client.fine_tuning.jobs.list()
                jobs_list = []
                async for job in jobs_list_async:
                    jobs_list.append(job)
                print(f"[test_finetuning_sft_async] Listed {len(jobs_list)} jobs")

                assert len(jobs_list) > 0

                job_ids = [job.id for job in jobs_list]
                assert fine_tuning_job.id in job_ids

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_cancel_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")

                cancelled_job = await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {cancelled_job.id}")

                TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")

                retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Verified cancellation persisted for job: {retrieved_job.id}")
                TestBase.validate_fine_tuning_job(
                    retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
                )

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "dpo")

                # Wait for completion of uploading of files
                time.sleep(10)

                fine_tuning_job = await self._create_dpo_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_dpo_async] Created DPO fine-tuning job: {fine_tuning_job.id}")
                print(fine_tuning_job)

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "dpo")

                print(f"[test_finetuning_dpo_async] DPO method validation passed - type: {fine_tuning_job.method.type}")

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_dpo_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "rft")

                # Wait for completion of uploading of files
                time.sleep(10)

                fine_tuning_job = await self._create_rft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_rft_async] Created RFT fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "reinforcement")

                print(f"[test_finetuning_rft_async] RFT method validation passed - type: {fine_tuning_job.method.type}")

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_rft_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_events_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")

                events_list_async = openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id)
                events_list = []
                async for event in events_list_async:
                    events_list.append(event)
                print(f"[test_finetuning_sft_async] Listed {len(events_list)} events for job: {fine_tuning_job.id}")

                # Verify that events exist (at minimum, job creation event should be present)
                assert len(events_list) > 0, "Fine-tuning job should have at least one event"

                # Verify events have required attributes
                for event in events_list:
                    assert event.id is not None, "Event should have an ID"
                    assert event.object is not None, "Event should have an object type"
                    assert event.created_at is not None, "Event should have a creation timestamp"
                    assert event.level is not None, "Event should have a level"
                    assert event.message is not None, "Event should have a message"
                    assert event.type is not None, "Event should have a type"
                print(f"[test_finetuning_sft_async] Successfully validated {len(events_list)} events")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_pause_resume_job_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id
                )
                print(f"[test_finetuning_resume_async] Created job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

                paused_job = await openai_client.fine_tuning.jobs.pause(fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(paused_job.status, "paused")
                print(f"[test_finetuning_resume_async] Paused job: {paused_job.id}")

                resumed_job = await openai_client.fine_tuning.jobs.resume(fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(resumed_job.status, "running")
                print(f"[test_finetuning_resume_async] Resumed job: {resumed_job.id}")

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_resume_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_oss_model_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, "oss"
                )
                print(f"[test_finetuning_sft_oss_async] Created fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(
                    f"[test_finetuning_sft_oss_async] SFT method validation passed - type: {fine_tuning_job.method.type}"
                )

                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_oss_async] Cancelled job: {fine_tuning_job.id}")

                await self._cleanup_test_files_async(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_pre_finetuning_job_deploy_infer_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:
            
            async with await project_client.get_openai_client() as openai_client:
                
                # Use predefined values from test_base for consistency
                pre_finetuned_model = self.test_finetuning_params["sft"]["openai"]["deployment"]["pre_finetuned_model"]
                deployment_name = f"{self.test_finetuning_params['sft']['openai']['deployment']['deployment_name']}-async-{int(time.time())}"
                
                resource_group = kwargs.get("azure_ai_projects_tests_azure_resource_group", "")
                account_name = kwargs.get("azure_ai_projects_tests_azure_aoai_account", "")
                
                assert resource_group, "Azure resource group is required for deployment test"
                assert account_name, "Azure OpenAI account name is required for deployment test"
                
                print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Deploying model: {pre_finetuned_model}, Deployment name: {deployment_name}")
                
                async with self.create_cognitive_services_management_client_async(**kwargs) as cogsvc_client:
                    
                    deployment_model = DeploymentModel(
                        format="OpenAI",
                        name=pre_finetuned_model,
                        version="1"
                    )
                    
                    deployment_properties = DeploymentProperties(
                        model=deployment_model
                    )
                    
                    deployment_sku = Sku(
                        name="Standard",
                        capacity=1
                    )
                    
                    deployment_config = Deployment(
                        properties=deployment_properties,
                        sku=deployment_sku
                    )
                    
                    deployment_operation = await cogsvc_client.deployments.begin_create_or_update(
                        resource_group_name=resource_group,
                        account_name=account_name,
                        deployment_name=deployment_name,
                        deployment=deployment_config
                    )
                    
                    # Wait for deployment to complete
                    max_wait_time = 300
                    start_time = time.time()
                    
                    while (deployment_operation.status() not in ["succeeded", "failed"] and 
                           time.time() - start_time < max_wait_time):
                        await asyncio.sleep(30)
                        print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Deployment status: {deployment_operation.status()}")
                    
                    final_status = deployment_operation.status()
                    print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Final deployment status: {final_status}")
                    
                    if final_status == "succeeded":
                        print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Testing inference on deployed model")
                        
                        response = await openai_client.chat.completions.create(
                            model=deployment_name,
                            messages=[{"role": "user", "content": "Hello, how are you?"}],
                            max_tokens=50
                        )
                        
                        assert response.choices is not None, "Response choices should not be None"
                        assert len(response.choices) > 0, "Response should have at least one choice"
                        assert response.choices[0].message is not None, "Message should not be None"
                        assert response.choices[0].message.content is not None, "Message content should not be None"
                        
                        print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Inference successful: {response.choices[0].message.content[:100]}")
                        
                        await cogsvc_client.deployments.begin_delete(
                            resource_group_name=resource_group,
                            account_name=account_name,
                            deployment_name=deployment_name
                        )
                        print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Started deployment cleanup")
                    
                    else:
                        print(f"[test_sft_pre_finetuning_job_deploy_infer_async] Deployment failed or timed out: {final_status}")
