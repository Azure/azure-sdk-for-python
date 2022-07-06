# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class PipelineJobSettings(object):
    """
    Settings of PipelineJob, include default_datastore, default_compute, continue_on_step_failure and force_rerun.

    :param default_datastore: The default datastore of pipeline.
    :type default_datastore: str
    :param default_compute: The default compute target of pipeline.
    :type default_compute: str
    :param continue_on_step_failure: Flag when set, continue pipeline execution if a step fails.
    :type continue_on_step_failure: bool
    :param force_rerun: Flag will force rerun pipeline execution after set.
    :type force_rerun: bool
    """

    def __init__(
        self,
        default_datastore: str = None,
        default_compute: str = None,
        continue_on_step_failure: bool = None,
        force_rerun: bool = None,
        **kwargs
    ):
        self.default_compute = default_compute
        self.default_datastore = default_datastore
        self.continue_on_step_failure = continue_on_step_failure
        self.force_rerun = force_rerun
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _to_dict(self):
        return {
            "default_compute": self.default_compute,
            "default_datastore": self.default_datastore,
            "continue_on_step_failure": self.continue_on_step_failure,
            "force_rerun": self.force_rerun,
        }
