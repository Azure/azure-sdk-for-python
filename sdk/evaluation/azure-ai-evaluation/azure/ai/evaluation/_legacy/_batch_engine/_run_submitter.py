# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import dataclasses
import sys
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, TextIO, Union

from ._run import Run, RunStatus
from ._trace import start_trace, is_collection_writeable
from ._run_storage import AbstractRunStorage, NoOpRunStorage
from ._logging import incremental_print, print_red_error
from ._config import BatchEngineConfig
from ._exceptions import BatchEngineValidationError
from ._engine import BatchEngine, BatchEngineError, BatchResult


class RunSubmitter:
    """Submits run to executor
    promptflow-devkit/promptflow/_sdk/_orchestrator/run_submitter.py

    THIS WILL BE REMOVED IN A FUTURE CODE UPDATE"""

    def __init__(self, config: BatchEngineConfig):
        # self._client = PFClient instance
        # self._config = PFClient config
        # self.run_operations = RunOperations instance

        # TODO ralphe: Use proper logger here. Old code did LoggerFactory.get_logger(__name__)
        self._config = config

    def submit(
        self,
        dynamic_callable: Callable,
        inputs: Sequence[Mapping[str, Any]],
        column_mapping: Mapping[str, str],
        *,
        name_prefix: Optional[str] = None,
        created_on: Optional[datetime] = None,
        storage_creator: Optional[Callable[[Run], AbstractRunStorage]] = None,
        **kwargs,
    ) -> Run:
        # The old code always spun up two threads here using a ThreadPoolExecutor:
        # 1. One thread essentially did nothing of value (since tracing was disabled, and we
        #    don't care about checking for the latest PromptFlow version number now)
        # 2. The other thread did the _run_bulk call. This was followed by a
        #    wait(return_when=ALL_COMPLETED)
        # This quite frankly is unnecessary complexity since the the evaluation code already
        # calls this in the context of ThreadPoolThread. So we can just do the equivalent
        # of the _run_bulk code here directly.
        # In a future code refactor, all of this will be cleaned up in favour of proper
        # async/await code.
        run: Run = kwargs.pop("run", None) or Run(
            dynamic_callable=dynamic_callable,
            name_prefix=name_prefix,
            inputs=inputs,
            column_mapping=column_mapping,
            created_on=created_on,
        )

        logger = self._config.logger
        attributes: Dict[str, Any] = kwargs.get("attributes", {})
        collection_for_run: Optional[str] = None

        logger.debug("start trace for flow run...")
        logger.debug("flow path for run.start_trace: %s", run.name)

        if is_collection_writeable():
            logger.debug("trace collection is writeable, will use flow name as collection...")
            collection_for_run = run.name
            logger.debug("collection for run: %s", collection_for_run)
        else:
            logger.debug("trace collection is protected, will honor existing collection.")
        start_trace(attributes=attributes, run=run, _collection=collection_for_run)

        self._validate_inputs(run=run)

        local_storage = storage_creator(run) if storage_creator else NoOpRunStorage()
        with local_storage.logger:
            run._status = RunStatus.PREPARING

            # unnecessary Flow loading code was removed here. Instead do direct calls to _submit_bulk_run
            self._submit_bulk_run(run=run, local_storage=local_storage, **kwargs)

        self.stream_run(run=run, storage=local_storage, raise_on_error=True)
        return run

    def _submit_bulk_run(self, run: Run, local_storage: AbstractRunStorage, **kwargs) -> None:
        logger = self._config.logger

        logger.info(f"Submitting run {run.name}, log path: {local_storage.logger.file_path}")

        # Old code loaded the Flex flow, parsed input and outputs types. That logic has been
        # removed since it is unnecessary. It also parsed and set environment variables. This
        # has also been removed since it can be problematic in a multi-threaded environment.

        self._validate_column_mapping(run.column_mapping)

        run._status = RunStatus.RUNNING
        run._start_time = datetime.now(timezone.utc)
        batch_result: Optional[BatchResult] = None

        try:
            batch_engine = BatchEngine(
                run.dynamic_callable,
                storage=local_storage,
                batch_timeout_sec=self._config.batch_timeout_seconds,
                line_timeout_sec=self._config.run_timeout_seconds,
                max_worker_count=self._config.max_concurrency,
                **kwargs,
            )

            batch_result = batch_engine.run(data=run.inputs, column_mapping=run.column_mapping, id=run.name)
            run._status = RunStatus.from_batch_result_status(batch_result.status)

            error_logs: Sequence[str] = []
            if run._status != RunStatus.COMPLETED:
                error_logs.append(f"Run {run.name} failed with status {batch_result.status}.")
                if batch_result.error:
                    error_logs.append(f"Error: {str(batch_result.error)}")

            if error_logs:
                logger.warning("\n".join(error_logs))
        except Exception as e:
            run._status = RunStatus.FAILED
            # when run failed in executor, store the exception in result and dump to file
            logger.warning(f"Run {run.name} failed when executing in executor with exception {e}.")
            # for user error, swallow stack trace and return failed run since user don't need the stack trace
            if not isinstance(e, BatchEngineValidationError):
                # for other errors, raise it to user to help debug root cause.
                raise e
            # won't raise the exception since it's already included in run object.
        finally:
            # persist inputs, outputs and metrics
            local_storage.persist_result(batch_result)
            # exceptions
            # local_storage.dump_exception(exception=exception, batch_result=batch_result) # TODO ralphe: persist_result should handle this
            # system metrics
            system_metrics = {}
            if batch_result:
                system_metrics.update(dataclasses.asdict(batch_result.tokens))  # token related
                system_metrics.update(
                    {
                        "duration": batch_result.duration.total_seconds(),
                        # "__pf__.lines.completed": batch_result.total_lines - batch_result.failed_lines,
                        # "__pf__.lines.failed": batch_result.failed_lines,
                    }
                )

            run._end_time = datetime.now(timezone.utc)
            run.metrics = system_metrics
            run.result = batch_result

    @staticmethod
    def _validate_inputs(run: Run):
        if not run.inputs:
            raise BatchEngineValidationError("Data must be specified for evaluation run.")

    @staticmethod
    def _validate_column_mapping(column_mapping: Mapping[str, str]):
        if not isinstance(column_mapping, Mapping):
            raise BatchEngineValidationError(f"Column mapping must be a dict, got {type(column_mapping)}.")

        has_mapping = any([isinstance(v, str) and v.startswith("$") for v in column_mapping.values()])
        if not has_mapping:
            raise BatchEngineValidationError(
                "Column mapping must contain at least one mapping binding, "
                f"current column mapping contains all static values: {column_mapping}"
            )

    @staticmethod
    def stream_run(run: Run, storage: AbstractRunStorage, raise_on_error: bool) -> None:
        """
        Stream the output of the batch execution.

        :param Run run: The run to stream.
        :param AbstractRunStorage storage: The storage to use for the output.
        """

        # TODO ralphe: This doesn't seem to be do anything useful beyond just print
        #              a run summary at the end. This is because by the time it gets
        #              invoked even in the original code, the run has already completed.

        if run is None or storage is None:
            return

        file_handler = sys.stdout
        try:
            printed = 0
            available_logs = storage.logger.get_logs()
            incremental_print(available_logs, printed, file_handler)
            RunSubmitter._print_run_summary(run, file_handler)
        except KeyboardInterrupt:
            error_message = "The output streaming for the run was interrupted, but the run is still executing."
            print(error_message)

        if run.status == RunStatus.FAILED or run.status == RunStatus.CANCELED:
            if run.status == RunStatus.FAILED:
                error_message = storage.load_exception().get("message", "Run fails with unknown error.")
            else:
                error_message = "Run is canceled."
            if raise_on_error:
                raise BatchEngineError(error_message)
            else:
                print_red_error(error_message)

    @staticmethod
    def _print_run_summary(run: Run, text_out: Union[TextIO, Any]) -> None:
        duration = str(run.duration)
        text_out.write(
            "======= Run Summary =======\n\n"
            f'Run name: "{run.name}"\n'
            f'Run status: "{run.status.value}"\n'
            f'Start time: "{run.created_on}"\n'
            f'Duration: "{duration}"\n\n'
        )
