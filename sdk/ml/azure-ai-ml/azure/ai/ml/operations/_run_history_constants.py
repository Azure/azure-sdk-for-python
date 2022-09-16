# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

# default timeout of session for getting content in the job run,
# the 1st element is conn timeout, the 2nd is the read timeout.


class JobStatus(object):
    """
    * NotStarted - This is a temporary state client-side Run objects are in before cloud submission.
    * Starting - The Run has started being processed in the cloud. The caller has a run ID at this point.
    * Provisioning - Returned when on-demand compute is being created for a given job submission.
    * Preparing - The run environment is being prepared:
        * docker image build
        * conda environment setup
    * Queued - The job is queued in the compute target. For example, in BatchAI the job is in queued state
            while waiting for all the requested nodes to be ready.
    * Running - The job started to run in the compute target.
    * Finalizing - User code has completed and the run is in post-processing stages.
    * CancelRequested - Cancellation has been requested for the job.
    * Completed - The run completed successfully. This includes both the user code and run
        post-processing stages.
    * Failed - The run failed. Usually the Error property on a run will provide details as to why.
    * Canceled - Follows a cancellation request and indicates that the run is now successfully cancelled.
    * NotResponding - For runs that have Heartbeats enabled, no heartbeat has been recently sent.
    """

    # Ordered by transition order
    QUEUED = "Queued"
    NOT_STARTED = "NotStarted"
    PREPARING = "Preparing"
    PROVISIONING = "Provisioning"
    STARTING = "Starting"
    RUNNING = "Running"
    CANCEL_REQUESTED = "CancelRequested"
    CANCELED = "Canceled"  # Not official yet
    FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PAUSED = "Paused"
    NOTRESPONDING = "NotResponding"


class RunHistoryConstants(object):
    _DEFAULT_GET_CONTENT_TIMEOUT = (5, 120)
    _WAIT_COMPLETION_POLLING_INTERVAL_MIN = os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MIN", 2)
    _WAIT_COMPLETION_POLLING_INTERVAL_MAX = os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MAX", 60)
    ALL_STATUSES = [
        JobStatus.QUEUED,
        JobStatus.PREPARING,
        JobStatus.PROVISIONING,
        JobStatus.STARTING,
        JobStatus.RUNNING,
        JobStatus.CANCEL_REQUESTED,
        JobStatus.CANCELED,
        JobStatus.FINALIZING,
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.NOT_STARTED,
        JobStatus.FAILED,
        JobStatus.PAUSED,
        JobStatus.NOTRESPONDING,
    ]
    IN_PROGRESS_STATUSES = [
        JobStatus.NOT_STARTED,
        JobStatus.QUEUED,
        JobStatus.PREPARING,
        JobStatus.PROVISIONING,
        JobStatus.STARTING,
        JobStatus.RUNNING,
    ]
    POST_PROCESSING_STATUSES = [JobStatus.CANCEL_REQUESTED, JobStatus.FINALIZING]
    TERMINAL_STATUSES = [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELED,
        JobStatus.NOTRESPONDING,
        JobStatus.PAUSED,
    ]
