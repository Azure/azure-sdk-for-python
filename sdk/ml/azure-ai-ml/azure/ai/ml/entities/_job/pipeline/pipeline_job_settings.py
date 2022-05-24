# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class PipelineJobSettings(object):
    def __init__(
        self,
        default_datastore: str = None,
        default_compute: str = None,
        continue_on_step_failure: bool = None,
        force_rerun: bool = False,
        **kwargs
    ):
        """Initialize a PipelineJobSettings instance

        :param default_datastore: The default datastore of pipeline.
        :type default_datastore: str
        :param default_compute: The compute target of pipeline.
        :type default_compute: str
        :param continue_on_step_failure: Flag when set, continue pipeline execution if a step fails.
        :type continue_on_step_failure: bool
        :param force_rerun: Flag when set, rerun pipeline execution.
        :type force_rerun: bool
        """

        self.default_compute = default_compute
        self.default_datastore = default_datastore
        self.continue_on_step_failure = continue_on_step_failure
        self.force_rerun = force_rerun
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return {
            "default_compute": self.default_compute,
            "default_datastore": self.default_datastore,
            "continue_on_step_failure": self.continue_on_step_failure,
            "force_rerun": self.force_rerun,
        }
