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
        train_processed_file = await openai_client.files.wait_for_processing(train_file.id)
        assert train_processed_file is not None
        assert train_processed_file.id is not None
        TestBase.assert_equal_or_not_none(train_processed_file.status, "processed")
        print(f"[test_finetuning_{job_type}_async] Uploaded training file: {train_processed_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
        validation_processed_file = await openai_client.files.wait_for_processing(validation_file.id)
        assert validation_processed_file is not None
        assert validation_processed_file.id is not None
        TestBase.assert_equal_or_not_none(validation_processed_file.status, "processed")
        print(f"[test_finetuning_{job_type}_async] Uploaded validation file: {validation_processed_file.id}")

        return train_processed_file, validation_processed_file

    async def _cleanup_test_files_async(self, openai_client, train_file, validation_file, job_type):
        """Helper method to clean up uploaded files after testing asynchronously."""
        await openai_client.files.delete(train_file.id)
        print(f"[test_finetuning_{job_type}_async] Deleted training file: {train_file.id}")

        await openai_client.files.delete(validation_file.id)
        print(f"[test_finetuning_{job_type}_async] Deleted validation file: {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_retrieve_job_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_jobs_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_cancel_job_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_dpo_finetuning_create_job_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "dpo")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "dpo")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_rft_finetuning_create_job_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "rft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "rft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_finetuning_list_events_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

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

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft")

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_sft_finetuning_create_job_oss_model_async(self, **kwargs):

        project_client = self.create_async_client(**kwargs)
        openai_client = project_client.get_openai_client()

        async with project_client:

            train_file, validation_file = await self._upload_test_files_async(openai_client, "sft")

            fine_tuning_job = await self._create_sft_finetuning_job_async(
                openai_client, train_file.id, validation_file.id, "oss"
            )
            print(f"[test_finetuning_sft_oss_async] Created fine-tuning job: {fine_tuning_job.id}")
            TestBase.validate_fine_tuning_job(
                fine_tuning_job, expected_model=self.test_finetuning_params["sft"]["oss"]["model_name"]
            )
            TestBase.validate_fine_tuning_job(fine_tuning_job)
            TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
            TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
            assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
            TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
            print(f"[test_finetuning_sft_oss_async] SFT method validation passed - type: {fine_tuning_job.method.type}")

            await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"[test_finetuning_sft_oss_async] Cancelled job: {fine_tuning_job.id}")

            await self._cleanup_test_files_async(openai_client, train_file, validation_file, "sft_oss")
