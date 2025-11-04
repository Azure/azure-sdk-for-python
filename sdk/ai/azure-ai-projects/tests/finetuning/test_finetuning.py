# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time
import pytest
from pathlib import Path
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording


@pytest.mark.skipif(
    condition=(not is_live_and_not_recording()),
    reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuning(TestBase):

    def _create_sft_finetuning_job(self, openai_client, train_file_id, validation_file_id, model_type="openai"):
        """Helper method to create a supervised fine-tuning job."""
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
        )

    def _create_dpo_finetuning_job(self, openai_client, train_file_id, validation_file_id):
        """Helper method to create a DPO fine-tuning job."""
        return openai_client.fine_tuning.jobs.create(
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

    def _create_rft_finetuning_job(self, openai_client, train_file_id, validation_file_id):
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

        return openai_client.fine_tuning.jobs.create(
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

    def _upload_test_files(self, openai_client, job_type="sft"):
        """Helper method to upload training and validation files for fine-tuning tests."""
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with open(training_file_path, "rb") as f:
            train_file = openai_client.files.create(file=f, purpose="fine-tune")
        assert train_file is not None
        assert train_file.id is not None
        TestBase.assert_equal_or_not_none(train_file.status, "pending")
        print(f"[test_finetuning_{job_type}] Uploaded training file: {train_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = openai_client.files.create(file=f, purpose="fine-tune")
        assert validation_file is not None
        assert validation_file.id is not None
        TestBase.assert_equal_or_not_none(validation_file.status, "pending")
        print(f"[test_finetuning_{job_type}] Uploaded validation file: {validation_file.id}")

        return train_file, validation_file

    def _cleanup_test_files(self, openai_client, train_file, validation_file):
        """Helper method to clean up uploaded files after testing."""
        openai_client.files.delete(train_file.id)
        print(f"Deleted training file: {train_file.id}")

        openai_client.files.delete(validation_file.id)
        print(f"Deleted validation file: {validation_file.id}")

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_finetuning_create_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft] Created fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(f"[test_finetuning_sft] SFT method validation passed - type: {fine_tuning_job.method.type}")

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_retrieve_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_list_jobs(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

                jobs_list = list(openai_client.fine_tuning.jobs.list())
                print(f"[test_finetuning_sft] Listed {len(jobs_list)} jobs")

                assert len(jobs_list) > 0

                job_ids = [job.id for job in jobs_list]
                assert fine_tuning_job.id in job_ids

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_cancel_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

                cancelled_job = openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {cancelled_job.id}")

                TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Verified cancellation persisted for job: {retrieved_job.id}")
                TestBase.validate_fine_tuning_job(
                    retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
                )

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_dpo_finetuning_create_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "dpo")

                # Wait for completion of uploading of files
                time.sleep(10)

                fine_tuning_job = self._create_dpo_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_dpo] Created DPO fine-tuning job: {fine_tuning_job.id}")
                print(fine_tuning_job)

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "dpo")

                print(f"[test_finetuning_dpo] DPO method validation passed - type: {fine_tuning_job.method.type}")

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_dpo] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_rft_finetuning_create_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "rft")

                # Wait for completion of uploading of files
                time.sleep(10)

                fine_tuning_job = self._create_rft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_rft] Created RFT fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "reinforcement")

                print(f"[test_finetuning_rft] RFT method validation passed - type: {fine_tuning_job.method.type}")

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_rft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_list_events(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

                events_list = list(openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id))
                print(f"[test_finetuning_sft] Listed {len(events_list)} events for job: {fine_tuning_job.id}")

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
                print(f"[test_finetuning_sft] Successfully validated {len(events_list)} events")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_pause_resume_job(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id)
                print(f"[test_finetuning_resume] Created job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)

                paused_job = openai_client.fine_tuning.jobs.pause(fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(paused_job.status, "paused")
                print(f"[test_finetuning_resume] Paused job: {paused_job.id}")

                resumed_job = openai_client.fine_tuning.jobs.resume(fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(resumed_job.status, "running")
                print(f"[test_finetuning_resume] Resumed job: {resumed_job.id}")

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_resume] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_finetuning_create_job_oss_model(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, "sft")

                # Wait for files to be processed
                time.sleep(10)

                fine_tuning_job = self._create_sft_finetuning_job(
                    openai_client, train_file.id, validation_file.id, "oss"
                )
                print(f"[test_finetuning_sft_oss] Created fine-tuning job: {fine_tuning_job.id}")

                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(f"[test_finetuning_sft_oss] SFT method validation passed - type: {fine_tuning_job.method.type}")

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft_oss] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_files(openai_client, train_file, validation_file)
