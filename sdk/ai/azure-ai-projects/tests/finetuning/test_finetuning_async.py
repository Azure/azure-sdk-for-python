# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from pathlib import Path
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording


@pytest.mark.skipif(
    condition=(not is_live_and_not_recording()),
    reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuningAsync(TestBase):
    
    SFT_JOB_TYPE = "sft"
    DPO_JOB_TYPE = "dpo"
    RFT_JOB_TYPE = "rft"
    
    STANDARD_TRAINING_TYPE = "Standard"
    GLOBAL_STANDARD_TRAINING_TYPE = "GlobalStandard"

    async def _create_sft_finetuning_job_async(
        self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"
    ):
        """Helper method to create a supervised fine-tuning job."""
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

    async def _create_dpo_finetuning_job_async(self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"):
        """Helper method to create a DPO fine-tuning job."""
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

    async def _create_rft_finetuning_job_async(self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"):
        """Helper method to create an RFT fine-tuning job."""
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

    async def _upload_test_files_async(self, openai_client, job_type="sft"):
        """Helper method to upload training and validation files for fine-tuning tests."""
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with open(training_file_path, "rb") as f:
            train_file = await openai_client.files.create(file=f, purpose="fine-tune")
        train_processed_file = await openai_client.files.wait_for_processing(train_file.id)
        assert train_processed_file is not None
        assert train_processed_file.id is not None
        TestBase.assert_equal_or_not_none(train_processed_file.status, "processed")
        print(f"[test_finetuning] Uploaded training file: {train_processed_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
        validation_processed_file = await openai_client.files.wait_for_processing(validation_file.id)
        assert validation_processed_file is not None
        assert validation_processed_file.id is not None
        TestBase.assert_equal_or_not_none(validation_processed_file.status, "processed")
        print(f"[test_finetuning] Uploaded validation file: {validation_processed_file.id}")

        return train_processed_file, validation_processed_file

    async def _cleanup_test_file_async(self, openai_client, file_id):
        """Helper method to clean up uploaded file."""
        await openai_client.files.delete(file_id)
        print(f"[test_finetuning] Deleted file: {file_id}")

    async def _test_cancel_job_helper_async(self, job_type, model_type, training_type, expected_method_type, **kwargs):
        """Helper method for testing canceling fine-tuning jobs across different configurations."""
        
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:
            
            train_file, validation_file = await self._upload_test_files_async(openai_client, job_type)
            
            if job_type == self.SFT_JOB_TYPE:
                fine_tuning_job = await self._create_sft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            elif job_type == self.DPO_JOB_TYPE:
                fine_tuning_job = await self._create_dpo_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            elif job_type == self.RFT_JOB_TYPE:
                fine_tuning_job = await self._create_rft_finetuning_job_async(
                    openai_client, train_file.id, validation_file.id, training_type, model_type
                )
            else:
                raise ValueError(f"Unsupported job type: {job_type}")
            
            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Created job: {fine_tuning_job.id}")
            
            cancelled_job = await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Cancelled job: {cancelled_job.id}")
            
            TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
            TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")
            TestBase.assert_equal_or_not_none(cancelled_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(cancelled_job.validation_file, validation_file.id)
            
            assert cancelled_job.method is not None, f"Method should not be None for {job_type} job"
            TestBase.assert_equal_or_not_none(cancelled_job.method.type, expected_method_type)
            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Method validation passed - type: {cancelled_job.method.type}")
            
            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Verified cancellation persisted for job: {retrieved_job.id}")
            TestBase.validate_fine_tuning_job(
                retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
            )
            
            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_sft_create_job_helper_async(self, model_type, training_type, **kwargs):
        """Helper method for testing SFT fine-tuning job creation across different configurations."""
        
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:
            
            train_file, validation_file = await self._upload_test_files_async(openai_client, self.SFT_JOB_TYPE)
            
            fine_tuning_job = await self._create_sft_finetuning_job_async(openai_client, train_file.id, validation_file.id, training_type, model_type)
            print(f"[test_finetuning_sft_{model_type}_{training_type}] Created fine-tuning job: {fine_tuning_job.id}")
            
            TestBase.validate_fine_tuning_job(fine_tuning_job)
            TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
            assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
            TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
            print(f"[test_finetuning_sft_{model_type}_{training_type}] SFT method validation passed - type: {fine_tuning_job.method.type}")
            
            if model_type == "oss":
                TestBase.validate_fine_tuning_job(
                    fine_tuning_job, expected_model=self.test_finetuning_params["sft"]["oss"]["model_name"]
                )
            
            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_sft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")
            
            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_dpo_create_job_helper_async(self, model_type, training_type, **kwargs):
        """Helper method for testing DPO fine-tuning job creation across different configurations."""
        
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:
            
            train_file, validation_file = await self._upload_test_files_async(openai_client, self.DPO_JOB_TYPE)
            
            fine_tuning_job = await self._create_dpo_finetuning_job_async(openai_client, train_file.id, validation_file.id, training_type, model_type)
            print(f"[test_finetuning_dpo_{model_type}_{training_type}] Created DPO fine-tuning job: {fine_tuning_job.id}")
            print(fine_tuning_job)
            
            TestBase.validate_fine_tuning_job(fine_tuning_job)
            TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
            assert fine_tuning_job.method is not None, "Method should not be None for DPO job"
            TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "dpo")
            
            print(f"[test_finetuning_dpo_{model_type}_{training_type}] DPO method validation passed - type: {fine_tuning_job.method.type}")
            
            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_dpo_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")
            
            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    async def _test_rft_create_job_helper_async(self, model_type, training_type, **kwargs):
        """Helper method for testing RFT fine-tuning job creation across different configurations."""
        
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:
            
            train_file, validation_file = await self._upload_test_files_async(openai_client, self.RFT_JOB_TYPE)
            
            fine_tuning_job = await self._create_rft_finetuning_job_async(openai_client, train_file.id, validation_file.id, training_type, model_type)
            print(f"[test_finetuning_rft_{model_type}_{training_type}] Created RFT fine-tuning job: {fine_tuning_job.id}")
            
            TestBase.validate_fine_tuning_job(fine_tuning_job)
            TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
            assert fine_tuning_job.method is not None, "Method should not be None for RFT job"
            TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "reinforcement")
            
            print(f"[test_finetuning_rft_{model_type}_{training_type}] RFT method validation passed - type: {fine_tuning_job.method.type}")
            
            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_rft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")
            
            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_openai_standard_async(self, **kwargs):
        """Test creating SFT fine-tuning job with OpenAI model and Standard training."""
        await self._test_sft_create_job_helper_async("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        """Test creating SFT fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_sft_create_job_helper_async("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_oss_globalstandard_async(self, **kwargs):
        """Test creating SFT fine-tuning job with OSS model and GlobalStandard training."""
        await self._test_sft_create_job_helper_async("oss", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_sft_job_async(self, **kwargs):
        """Test retrieving SFT fine-tuning job."""
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, self.SFT_JOB_TYPE)

            fine_tuning_job = await self._create_sft_finetuning_job_async(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
            print(f"[test_finetuning_retrieve_sft] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_sft] Retrieved job: {retrieved_job.id}")

            TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
            TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
            assert retrieved_job.method is not None, "Method should not be None for SFT job"
            TestBase.assert_equal_or_not_none(retrieved_job.method.type, "supervised")
            assert self.test_finetuning_params["sft"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['sft']['openai']['model_name']} not found in {retrieved_job.model}"

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_sft] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_dpo_job_async(self, **kwargs):
        """Test retrieving DPO fine-tuning job."""
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, self.DPO_JOB_TYPE)

            fine_tuning_job = await self._create_dpo_finetuning_job_async(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
            print(f"[test_finetuning_retrieve_dpo] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_dpo] Retrieved job: {retrieved_job.id}")

            TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
            TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
            assert retrieved_job.method is not None, "Method should not be None for DPO job"
            TestBase.assert_equal_or_not_none(retrieved_job.method.type, "dpo")
            assert self.test_finetuning_params["dpo"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['dpo']['openai']['model_name']} not found in {retrieved_job.model}"

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_dpo] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_file_async(openai_client, train_file.id)
            await self._cleanup_test_file_async(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_rft_job_async(self, **kwargs):
        """Test retrieving RFT fine-tuning job."""
        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, self.RFT_JOB_TYPE)

            fine_tuning_job = await self._create_rft_finetuning_job_async(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
            print(f"[test_finetuning_retrieve_rft] Created job: {fine_tuning_job.id}")

            retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(f"[test_finetuning_retrieve_rft] Retrieved job: {retrieved_job.id}")

            TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
            TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
            TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
            assert retrieved_job.method is not None, "Method should not be None for RFT job"
            TestBase.assert_equal_or_not_none(retrieved_job.method.type, "reinforcement")
            assert self.test_finetuning_params["rft"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['rft']['openai']['model_name']} not found in {retrieved_job.model}"

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
        """Test canceling SFT fine-tuning job with OpenAI model and Standard training."""
        await self._test_cancel_job_helper_async(self.SFT_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_cancel_job_openai_globalstandard_async(self, **kwargs):
        """Test canceling SFT fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_cancel_job_helper_async(self.SFT_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_cancel_job_oss_globalstandard_async(self, **kwargs):
        """Test canceling SFT fine-tuning job with OSS model and GlobalStandard training."""
        await self._test_cancel_job_helper_async(self.SFT_JOB_TYPE, "oss", self.GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_cancel_job_openai_standard_async(self, **kwargs):
        """Test canceling DPO fine-tuning job with OpenAI model and Standard training."""
        await self._test_cancel_job_helper_async(self.DPO_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_cancel_job_openai_globalstandard_async(self, **kwargs):
        """Test canceling DPO fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_cancel_job_helper_async(self.DPO_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_cancel_job_openai_standard_async(self, **kwargs):
        """Test canceling RFT fine-tuning job with OpenAI model and Standard training."""
        await self._test_cancel_job_helper_async(self.RFT_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_cancel_job_openai_globalstandard_async(self, **kwargs):
        """Test canceling RFT fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_cancel_job_helper_async(self.RFT_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_openai_standard_async(self, **kwargs):
        """Test creating DPO fine-tuning job with OpenAI model and Standard training."""
        await self._test_dpo_create_job_helper_async("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        """Test creating DPO fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_dpo_create_job_helper_async("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_openai_standard_async(self, **kwargs):
        """Test creating RFT fine-tuning job with OpenAI model and Standard training."""
        await self._test_rft_create_job_helper_async("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_openai_globalstandard_async(self, **kwargs):
        """Test creating RFT fine-tuning job with OpenAI model and GlobalStandard training."""
        await self._test_rft_create_job_helper_async("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_events_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, self.SFT_JOB_TYPE)

            fine_tuning_job = await self._create_sft_finetuning_job_async(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
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
