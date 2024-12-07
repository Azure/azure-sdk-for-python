class TestCustomModelFineTuningJobSchema:

    def test_maas_finetuning_job_rest_roundtrip(
        self,
        expected_maas_finetuning_job,
        maas_finetuning_job,
    ):
        assert expected_maas_finetuning_job == maas_finetuning_job

    def test_maap_finetuning_job_compute_rest_roundtrip(
        self, expected_maap_finetuning_job_compute, maap_finetuning_job_compute
    ):
        assert expected_maap_finetuning_job_compute == maap_finetuning_job_compute

    def test_maap_finetuning_job_instance_types_rest_roundtrip(
        self, expected_maap_finetuning_job_instance_types, maap_finetuning_job_instance_types
    ):
        assert expected_maap_finetuning_job_instance_types == maap_finetuning_job_instance_types

    def test_maap_finetuning_job_queue_settings_rest_roundtrip(
        self,
        expected_maap_finetuning_job_queue_settings,
        maap_finetuning_job_queue_settings,
    ):
        assert expected_maap_finetuning_job_queue_settings == maap_finetuning_job_queue_settings
