# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from pathlib import Path
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording


@pytest.mark.skipif(
    condition=(not is_live_and_not_recording()),
    reason="Skipped because we cannot record network calls with AOAI client",
)
class TestFineTuning(TestBase):
    
    SFT_JOB_TYPE = "sft"
    DPO_JOB_TYPE = "dpo"
    RFT_JOB_TYPE = "rft"
    
    STANDARD_TRAINING_TYPE = "Standard"
    GLOBAL_STANDARD_TRAINING_TYPE = "GlobalStandard"

    def _create_sft_finetuning_job(
        self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"
    ):
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
            extra_body={"trainingType": training_type},
        )

    def _create_dpo_finetuning_job(self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"):
        """Helper method to create a DPO fine-tuning job."""
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

    def _create_rft_finetuning_job(self, openai_client, train_file_id, validation_file_id, training_type, model_type="openai"):
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

    def _upload_test_files(self, openai_client, job_type="sft"):
        """Helper method to upload training and validation files for fine-tuning tests."""
        test_data_dir = Path(__file__).parent.parent / "test_data" / "finetuning"
        training_file_path = test_data_dir / self.test_finetuning_params[job_type]["training_file_name"]
        validation_file_path = test_data_dir / self.test_finetuning_params[job_type]["validation_file_name"]

        with open(training_file_path, "rb") as f:
            train_file = openai_client.files.create(file=f, purpose="fine-tune")
        train_processed_file = openai_client.files.wait_for_processing(train_file.id)
        assert train_processed_file is not None
        assert train_processed_file.id is not None
        TestBase.assert_equal_or_not_none(train_processed_file.status, "processed")
        print(f"[test_finetuning] Uploaded training file: {train_processed_file.id}")

        with open(validation_file_path, "rb") as f:
            validation_file = openai_client.files.create(file=f, purpose="fine-tune")
        validation_processed_file = openai_client.files.wait_for_processing(validation_file.id)
        assert validation_processed_file is not None
        assert validation_processed_file.id is not None
        TestBase.assert_equal_or_not_none(validation_processed_file.status, "processed")
        print(f"[test_finetuning] Uploaded validation file: {validation_processed_file.id}")

        return train_processed_file, validation_processed_file

    def _cleanup_test_file(self, openai_client, file_id):
        """Helper method to clean up uploaded file."""
        openai_client.files.delete(file_id)
        print(f"[test_finetuning] Deleted file: {file_id}")

    def _test_cancel_job_helper(self, job_type, model_type, training_type, expected_method_type, **kwargs):
        """Helper method for testing canceling fine-tuning jobs across different configurations."""
        
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:
                
                train_file, validation_file = self._upload_test_files(openai_client, job_type)
                
                if job_type == self.SFT_JOB_TYPE:
                    fine_tuning_job = self._create_sft_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                elif job_type == self.DPO_JOB_TYPE:
                    fine_tuning_job = self._create_dpo_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                elif job_type == self.RFT_JOB_TYPE:
                    fine_tuning_job = self._create_rft_finetuning_job(
                        openai_client, train_file.id, validation_file.id, training_type, model_type
                    )
                else:
                    raise ValueError(f"Unsupported job type: {job_type}")
                
                print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Created job: {fine_tuning_job.id}")
                
                cancelled_job = openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Cancelled job: {cancelled_job.id}")
                
                # Validate the cancelled job
                TestBase.validate_fine_tuning_job(cancelled_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(cancelled_job.status, "cancelled")
                TestBase.assert_equal_or_not_none(cancelled_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(cancelled_job.validation_file, validation_file.id)
                
                # Validate method type
                assert cancelled_job.method is not None, f"Method should not be None for {job_type} job"
                TestBase.assert_equal_or_not_none(cancelled_job.method.type, expected_method_type)
                print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Method validation passed - type: {cancelled_job.method.type}")
                
                # Verify cancellation persisted by retrieving the job
                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_cancel_{job_type}_{model_type}_{training_type}] Verified cancellation persisted for job: {retrieved_job.id}")
                TestBase.validate_fine_tuning_job(
                    retrieved_job, expected_job_id=fine_tuning_job.id, expected_status="cancelled"
                )
                
                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _test_sft_create_job_helper(self, model_type, training_type, **kwargs):
        """Helper method for testing SFT fine-tuning job creation across different configurations."""
        
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:
                
                train_file, validation_file = self._upload_test_files(openai_client, self.SFT_JOB_TYPE)
                
                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id, training_type, model_type)
                print(f"[test_finetuning_sft_{model_type}_{training_type}] Created fine-tuning job: {fine_tuning_job.id}")
                
                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "supervised")
                print(f"[test_finetuning_sft_{model_type}_{training_type}] SFT method validation passed - type: {fine_tuning_job.method.type}")
                
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
        """Helper method for testing DPO fine-tuning job creation across different configurations."""
        
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:
                
                train_file, validation_file = self._upload_test_files(openai_client, self.DPO_JOB_TYPE)
                
                fine_tuning_job = self._create_dpo_finetuning_job(openai_client, train_file.id, validation_file.id, training_type, model_type)
                print(f"[test_finetuning_dpo_{model_type}_{training_type}] Created DPO fine-tuning job: {fine_tuning_job.id}")
                print(fine_tuning_job)
                
                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "dpo")
                
                print(f"[test_finetuning_dpo_{model_type}_{training_type}] DPO method validation passed - type: {fine_tuning_job.method.type}")
                
                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_dpo_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")
                
                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    def _test_rft_create_job_helper(self, model_type, training_type, **kwargs):
        """Helper method for testing RFT fine-tuning job creation across different configurations."""
        
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:
                
                train_file, validation_file = self._upload_test_files(openai_client, self.RFT_JOB_TYPE)
                
                fine_tuning_job = self._create_rft_finetuning_job(openai_client, train_file.id, validation_file.id, training_type, model_type)
                print(f"[test_finetuning_rft_{model_type}_{training_type}] Created RFT fine-tuning job: {fine_tuning_job.id}")
                
                TestBase.validate_fine_tuning_job(fine_tuning_job)
                TestBase.assert_equal_or_not_none(fine_tuning_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(fine_tuning_job.trainingType.lower(), training_type.lower())
                assert fine_tuning_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(fine_tuning_job.method.type, "reinforcement")
                
                print(f"[test_finetuning_rft_{model_type}_{training_type}] RFT method validation passed - type: {fine_tuning_job.method.type}")
                
                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_rft_{model_type}_{training_type}] Cancelled job: {fine_tuning_job.id}")
                
                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_finetuning_create_job_openai_standard(self, **kwargs):
        """Test creating SFT fine-tuning job with OpenAI model and Standard training."""
        self._test_sft_create_job_helper("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_finetuning_create_job_openai_globalstandard(self, **kwargs):
        """Test creating SFT fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_sft_create_job_helper("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_finetuning_create_job_oss_globalstandard(self, **kwargs):
        """Test creating SFT fine-tuning job with OSS model and GlobalStandard training."""
        self._test_sft_create_job_helper("oss", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_retrieve_sft_job(self, **kwargs):
        """Test retrieving SFT fine-tuning job."""
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, self.SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
                print(f"[test_finetuning_retrieve_sft] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_sft] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for SFT job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "supervised")
                assert self.test_finetuning_params["sft"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['sft']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_retrieve_dpo_job(self, **kwargs):
        """Test retrieving DPO fine-tuning job."""
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, self.DPO_JOB_TYPE)

                fine_tuning_job = self._create_dpo_finetuning_job(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
                print(f"[test_finetuning_retrieve_dpo] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_dpo] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for DPO job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "dpo")
                assert self.test_finetuning_params["dpo"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['dpo']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_dpo] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_retrieve_rft_job(self, **kwargs):
        """Test retrieving RFT fine-tuning job."""
        with self.create_client(**kwargs) as project_client:
            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, self.RFT_JOB_TYPE)

                fine_tuning_job = self._create_rft_finetuning_job(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
                print(f"[test_finetuning_retrieve_rft] Created job: {fine_tuning_job.id}")

                retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_rft] Retrieved job: {retrieved_job.id}")

                TestBase.validate_fine_tuning_job(retrieved_job, expected_job_id=fine_tuning_job.id)
                TestBase.assert_equal_or_not_none(retrieved_job.training_file, train_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.validation_file, validation_file.id)
                TestBase.assert_equal_or_not_none(retrieved_job.trainingType.lower(), self.STANDARD_TRAINING_TYPE.lower())
                assert retrieved_job.method is not None, "Method should not be None for RFT job"
                TestBase.assert_equal_or_not_none(retrieved_job.method.type, "reinforcement")
                assert self.test_finetuning_params["rft"]["openai"]["model_name"] in retrieved_job.model, f"Expected model name {self.test_finetuning_params['rft']['openai']['model_name']} not found in {retrieved_job.model}"

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_retrieve_rft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_list_jobs(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, self.SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
                print(f"[test_finetuning_sft] Created job: {fine_tuning_job.id}")

                jobs_list = list(openai_client.fine_tuning.jobs.list())
                print(f"[test_finetuning_sft] Listed {len(jobs_list)} jobs")

                assert len(jobs_list) > 0

                job_ids = [job.id for job in jobs_list]
                assert fine_tuning_job.id in job_ids

                openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"[test_finetuning_sft] Cancelled job: {fine_tuning_job.id}")

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)

    

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_cancel_job_openai_standard(self, **kwargs):
        """Test canceling SFT fine-tuning job with OpenAI model and Standard training."""
        self._test_cancel_job_helper(self.SFT_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_cancel_job_openai_globalstandard(self, **kwargs):
        """Test canceling SFT fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_cancel_job_helper(self.SFT_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_sft_cancel_job_oss_globalstandard(self, **kwargs):
        """Test canceling SFT fine-tuning job with OSS model and GlobalStandard training."""
        self._test_cancel_job_helper(self.SFT_JOB_TYPE, "oss", self.GLOBAL_STANDARD_TRAINING_TYPE, "supervised", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_dpo_cancel_job_openai_standard(self, **kwargs):
        """Test canceling DPO fine-tuning job with OpenAI model and Standard training."""
        self._test_cancel_job_helper(self.DPO_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_dpo_cancel_job_openai_globalstandard(self, **kwargs):
        """Test canceling DPO fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_cancel_job_helper(self.DPO_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "dpo", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_rft_cancel_job_openai_standard(self, **kwargs):
        """Test canceling RFT fine-tuning job with OpenAI model and Standard training."""
        self._test_cancel_job_helper(self.RFT_JOB_TYPE, "openai", self.STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_rft_cancel_job_openai_globalstandard(self, **kwargs):
        """Test canceling RFT fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_cancel_job_helper(self.RFT_JOB_TYPE, "openai", self.GLOBAL_STANDARD_TRAINING_TYPE, "reinforcement", **kwargs)

    

    @servicePreparer()
    @recorded_by_proxy
    def test_dpo_finetuning_create_job_openai_standard(self, **kwargs):
        """Test creating DPO fine-tuning job with OpenAI model and Standard training."""
        self._test_dpo_create_job_helper("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_dpo_finetuning_create_job_openai_globalstandard(self, **kwargs):
        """Test creating DPO fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_dpo_create_job_helper("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    

    @servicePreparer()
    @recorded_by_proxy
    def test_rft_finetuning_create_job_openai_standard(self, **kwargs):
        """Test creating RFT fine-tuning job with OpenAI model and Standard training."""
        self._test_rft_create_job_helper("openai", self.STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_rft_finetuning_create_job_openai_globalstandard(self, **kwargs):
        """Test creating RFT fine-tuning job with OpenAI model and GlobalStandard training."""
        self._test_rft_create_job_helper("openai", self.GLOBAL_STANDARD_TRAINING_TYPE, **kwargs)

    @servicePreparer()
    @recorded_by_proxy
    def test_finetuning_list_events(self, **kwargs):

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                train_file, validation_file = self._upload_test_files(openai_client, self.SFT_JOB_TYPE)

                fine_tuning_job = self._create_sft_finetuning_job(openai_client, train_file.id, validation_file.id, self.STANDARD_TRAINING_TYPE)
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

                self._cleanup_test_file(openai_client, train_file.id)
                self._cleanup_test_file(openai_client, validation_file.id)


