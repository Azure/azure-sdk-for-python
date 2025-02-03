from azure.ai.ml.entities import CustomModelFineTuningJob
from azure.ai.ml.operations._run_history_constants import JobStatus


def validate_job(
    input_job: CustomModelFineTuningJob,
    created_job: CustomModelFineTuningJob,
    returned_job: CustomModelFineTuningJob,
) -> None:

    assert input_job is not None
    assert returned_job is not None
    assert created_job.id is not None
    assert created_job.name == input_job.name, f"Expected job name to be {created_job.name}"
    assert (
        input_job.display_name == created_job.display_name == returned_job.display_name
    ), f"Expected display name to be {input_job.display_name}"
    assert (
        input_job.experiment_name == created_job.experiment_name == returned_job.experiment_name
    ), "Expected experiment name to be {input_job.experiment_name}"
    assert created_job.status == JobStatus.RUNNING

    if input_job.resources:
        assert (
            input_job.resources.instance_types
            == created_job.resources.instance_types
            == returned_job.resources.instance_types
        )

    if input_job.queue_settings:
        assert (
            input_job.queue_settings.job_tier.lower()
            == created_job.queue_settings.job_tier.lower()
            == returned_job.queue_settings.job_tier.lower()
        )

    if input_job.compute:
        assert input_job.compute == created_job.compute == returned_job.compute
