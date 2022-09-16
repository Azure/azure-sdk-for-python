# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, MlException

from ._studio_url_from_job_id import studio_url_from_job_id


class JobParsingError(MlException):
    """Exception that the job data returned by MFE cannot be parsed."""

    def __init__(self, error_category, no_personal_data_message, message, *args, **kwargs):
        super(JobParsingError, self).__init__(
            message=message,
            target=ErrorTarget.JOB,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class PipelineChildJobError(MlException):
    """Exception that the pipeline child job is not supported."""

    ERROR_MESSAGE_TEMPLATE = "az ml job {command} is not supported on pipeline child job, {prompt_message}."
    PROMPT_STUDIO_UI_MESSAGE = "please go to studio UI to do related actions{url}"
    PROMPT_PARENT_MESSAGE = "please use this command on pipeline parent job"

    def __init__(self, job_id: str, command: str = "parse", prompt_studio_ui: bool = False):
        if prompt_studio_ui:
            url = studio_url_from_job_id(job_id)
            if url:
                url = f": {url}"
            prompt_message = self.PROMPT_STUDIO_UI_MESSAGE.format(url=url)
        else:
            prompt_message = self.PROMPT_PARENT_MESSAGE

        super(PipelineChildJobError, self).__init__(
            message=self.ERROR_MESSAGE_TEMPLATE.format(command=command, prompt_message=prompt_message),
            no_personal_data_message="Pipeline child job is not supported currently.",
            target=ErrorTarget.JOB,
            error_category=ErrorCategory.USER_ERROR,
        )
        self.job_id = job_id
