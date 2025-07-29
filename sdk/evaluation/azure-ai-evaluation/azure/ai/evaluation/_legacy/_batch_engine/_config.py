# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from logging import Logger

from ..._constants import PF_BATCH_TIMEOUT_SEC_DEFAULT


@dataclass
class BatchEngineConfig:
    """Context for a batch of evaluations. This will contain the configuration,
    logging, and other needed information."""

    logger: Logger
    """The logger to use for logging messages."""

    batch_timeout_seconds: int = PF_BATCH_TIMEOUT_SEC_DEFAULT
    """The maximum amount of time to wait for all evaluations in the batch to complete."""

    run_timeout_seconds: int = 600
    """The maximum amount of time to wait for an evaluation to run against a single entry
    in the data input to complete."""

    max_concurrency: int = 10
    """The maximum number of evaluations to run concurrently."""

    use_async: bool = True
    """Whether to use asynchronous evaluation."""

    default_num_results: int = 100
    """The default number of results to return if you don't ask for all results."""

    def __post_init__(self):
        if self.logger is None:
            raise ValueError("logger cannot be None")
        if self.batch_timeout_seconds <= 0:
            raise ValueError("batch_timeout_seconds must be greater than 0")
        if self.run_timeout_seconds <= 0:
            raise ValueError("run_timeout_seconds must be greater than 0")
        if self.max_concurrency <= 0:
            raise ValueError("max_concurrency must be greater than 0")
        if self.default_num_results <= 0:
            raise ValueError("default_num_results must be greater than 0")
