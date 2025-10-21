# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time
import pytest
from pathlib import Path
from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording


@pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuningSFTAsync(TestBase):

    async def _create_fine_tuning_job_async(self, openai_client, train_file_id, validation_file_id):
        """Helper method to create a supervised fine-tuning job asynchronously."""
        return await openai_client.fine_tuning.jobs.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model=self.test_finetuning_params["model_name"],
            method={
                "type": "supervised",
                "supervised": {
                    "hyperparameters": {
                        "n_epochs": self.test_finetuning_params["n_epochs"],
                        "batch_size": self.test_finetuning_params["batch_size"],
                        "learning_rate_multiplier": self.test_finetuning_params["learning_rate_multiplier"]
                    }
                }
            }
        )

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_sft_create_job_async(self, **kwargs):
        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        
        # Get the path to the test data files
        test_data_dir = Path(__file__).parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params["validation_file_name"]
        
        async with AIProjectClient(endpoint=endpoint, credential=self.get_credential(AIProjectClient, is_async=True)) as project_client:
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as openai_client:
                # Upload training file
                with open(training_file_path, "rb") as f:
                    train_file = await openai_client.files.create(file=f, purpose="fine-tune")
                assert train_file is not None
                assert train_file.id is not None
                TestBase.assert_equal_or_not_none(train_file.status, "pending")
                print(f"[test_finetuning_sft_async] Uploaded training file: {train_file.id}")
                
                # Upload validation file
                with open(validation_file_path, "rb") as f:
                    validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
                assert validation_file is not None
                assert validation_file.id is not None
                TestBase.assert_equal_or_not_none(validation_file.status, "pending")
                print(f"[test_finetuning_sft_async] Uploaded validation file: {validation_file.id}")

                # Wait for completion the uploading of files
                time.sleep(10)
                
                # Create a supervised fine-tuning job
                fine_tuning_job = await self._create_fine_tuning_job_async(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft_async] Created fine-tuning job: {fine_tuning_job.id}")
                
                # Validate the created job
                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                
                # Clean up: cancel the job
                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")
                
                # Clean up: delete the uploaded files
                await openai_client.files.delete(train_file.id)
                await openai_client.files.delete(validation_file.id)
                print(f"[test_finetuning_sft_async] Deleted files: {train_file.id}, {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_sft_retrieve_job_async(self, **kwargs):
        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        
        # Get the path to the test data files
        test_data_dir = Path(__file__).parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params["validation_file_name"]
        
        async with AIProjectClient(endpoint=endpoint, credential=self.get_credential(AIProjectClient, is_async=True)) as project_client:
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as openai_client:
                # Upload training file
                with open(training_file_path, "rb") as f:
                    train_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded training file: {train_file.id}")

                # Upload validation file
                with open(validation_file_path, "rb") as f:
                    validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded validation file: {validation_file.id}")

                # Wait for files to be processed
                time.sleep(10)
                
                # Create a supervised fine-tuning job
                fine_tuning_job = await self._create_fine_tuning_job_async(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")
                
                # Retrieve the job by ID
                retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Retrieved job: {retrieved_job.id}")
                
                # Validate the retrieved job
                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                
                # Clean up: cancel the job
                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")
                
                # Clean up: delete the uploaded files
                await openai_client.files.delete(train_file.id)
                await openai_client.files.delete(validation_file.id)
                print(f"[test_finetuning_sft_async] Deleted files: {train_file.id}, {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_sft_list_jobs_async(self, **kwargs):
        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        
        # Get the path to the test data files
        test_data_dir = Path(__file__).parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params["validation_file_name"]
        
        async with AIProjectClient(endpoint=endpoint, credential=self.get_credential(AIProjectClient, is_async=True)) as project_client:
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as openai_client:
                # Upload training file
                with open(training_file_path, "rb") as f:
                    train_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded training file: {train_file.id}")

                # Upload validation file
                with open(validation_file_path, "rb") as f:
                    validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded validation file: {validation_file.id}")

                # Wait for files to be processed
                time.sleep(10)
                
                # Create a supervised fine-tuning job
                fine_tuning_job = await self._create_fine_tuning_job_async(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")
                
                # List all fine-tuning jobs
                jobs_list_async = openai_client.fine_tuning.jobs.list()
                jobs_list = []
                async for job in jobs_list_async:
                    jobs_list.append(job)
                print(f"[test_finetuning_sft_async] Listed {len(jobs_list)} jobs")
                
                # Verify the list contains jobs
                assert len(jobs_list) > 0
                
                # Verify our created job is in the list
                job_ids = [job.id for job in jobs_list]
                assert fine_tuning_job.id in job_ids
                
                # Clean up: cancel the job
                await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {fine_tuning_job.id}")
                
                # Clean up: delete the uploaded files
                await openai_client.files.delete(train_file.id)
                await openai_client.files.delete(validation_file.id)
                print(f"[test_finetuning_sft_async] Deleted files: {train_file.id}, {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_sft_cancel_job_async(self, **kwargs):
        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        
        # Get the path to the test data files
        test_data_dir = Path(__file__).parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params["validation_file_name"]
        
        async with AIProjectClient(endpoint=endpoint, credential=self.get_credential(AIProjectClient, is_async=True)) as project_client:
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as openai_client:
                # Upload training file
                with open(training_file_path, "rb") as f:
                    train_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded training file: {train_file.id}")

                # Upload validation file
                with open(validation_file_path, "rb") as f:
                    validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"[test_finetuning_sft_async] Uploaded validation file: {validation_file.id}")
                
                # Wait for files to be processed
                time.sleep(10)
                
                # Create a supervised fine-tuning job
                fine_tuning_job = await self._create_fine_tuning_job_async(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft_async] Created job: {fine_tuning_job.id}")
                
                # Cancel the job
                cancelled_job = await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Cancelled job: {cancelled_job.id}")
                
                # Validate the cancelled job
                TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")
                
                # Verify cancellation persists by retrieving the job again
                retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft_async] Verified cancellation persisted for job: {retrieved_job.id}")
                TestBase.validate_fine_tuning_job(
                    retrieved_job,
                    expected_job_id=fine_tuning_job.id,
                    expected_status="cancelled"
                )
                
                # Clean up: delete the uploaded files
                await openai_client.files.delete(train_file.id)
                await openai_client.files.delete(validation_file.id)
                print(f"[test_finetuning_sft_async] Deleted files: {train_file.id}, {validation_file.id}")