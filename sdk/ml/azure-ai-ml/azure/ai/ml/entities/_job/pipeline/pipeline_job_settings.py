# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Generator, Optional

from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict


class PipelineJobSettings(_AttrDict):
    """Settings of PipelineJob.

    :param default_datastore: The default datastore of the pipeline.
    :type default_datastore: str
    :param default_compute: The default compute target of the pipeline.
    :type default_compute: str
    :param continue_on_step_failure: Flag indicating whether to continue pipeline execution if a step fails.
    :type continue_on_step_failure: bool
    :param force_rerun: Flag indicating whether to force rerun pipeline execution.
    :type force_rerun: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_pipeline_job_configurations.py
            :start-after: [START configure_pipeline_job_and_settings]
            :end-before: [END configure_pipeline_job_and_settings]
            :language: python
            :dedent: 8
            :caption: Shows how to set pipeline properties using this class.
    """

    def __init__(
        self,
        default_datastore: Optional[str] = None,
        default_compute: Optional[str] = None,
        continue_on_step_failure: Optional[bool] = None,
        force_rerun: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self._init = True
        super().__init__()
        self.default_compute: Any = default_compute
        self.default_datastore: Any = default_datastore
        self.continue_on_step_failure = continue_on_step_failure
        self.force_rerun = force_rerun
        self.on_init = kwargs.get("on_init", None)
        self.on_finalize = kwargs.get("on_finalize", None)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._init = False

    def _get_valid_keys(self) -> Generator[str, Any, None]:
        for k, v in self.__dict__.items():
            if v is None:
                continue
            # skip private attributes inherited from _AttrDict
            if k in ["_logger", "_allowed_keys", "_init", "_key_restriction"]:
                continue
            yield k

    def _to_dict(self) -> Dict:
        result = {}
        for k in self._get_valid_keys():
            result[k] = self.__dict__[k]
        result.update(self._get_attrs())
        return result

    def _initializing(self) -> bool:
        return self._init

    def __bool__(self) -> bool:
        for _ in self._get_valid_keys():
            return True
        # _attr_dict will return False if no extra attributes are set
        return self.__len__() > 0
