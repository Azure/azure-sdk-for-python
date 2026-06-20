# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This contains code merged together from the following files:
# promptflow-devkit/promptflow/batch/_batch_engine.py
# promptflow-devkit/promptflow/_proxy/_python_executor_proxy.py
# promptflow-core/promptflow/executor/_script_executor.py
# TODO ralphe: The way this code does batch execution needs to be improved. For now
#              porting over the code largely as is to remove the Promptflow dependency
#              as quickly as possible. In phase 2 this code will be heavily refactored.

import inspect
import re
import asyncio

from math import floor
from asyncio import Semaphore
from concurrent.futures import Executor
from functools import partial
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    cast,
    Literal,
)
from uuid import uuid4

from ._config import BatchEngineConfig
from ._utils import DEFAULTS_KEY, get_int_env_var, get_value_from_path, is_async_callable
from ._status import BatchStatus
from ._result import BatchResult, BatchRunDetails, BatchRunError, TokenMetrics
from ._run_storage import AbstractRunStorage, NoOpRunStorage
from .._common._logging import log_progress, logger, NodeLogManager
from ..._exceptions import ErrorBlame, EvaluationException
from ._exceptions import (
    BatchEngineCanceledError,
    BatchEngineError,
    BatchEngineRunFailedError,
    BatchEngineTimeoutError,
    BatchEngineValidationError,
)
from ._utils_deprecated import (
    async_run_allowing_running_loop,
    convert_eager_flow_output_to_dict,
)
from ._openai_injector import CaptureOpenAITokenUsage


MAX_WORKER_COUNT: Final[int] = 10
KEYWORD_PATTERN: Final = re.compile(r"^\${([^{}]+)}$")


class BatchEngine:
    """This class is used to execute flows in batch mode"""

    def __init__(
        self,
        func: Callable,
        *,
        config: BatchEngineConfig,
        storage: Optional[AbstractRunStorage] = None,
        executor: Optional[Executor] = None,
    ):
        """Create a new batch engine instance

        :param Callable func: The function to run the flow
        :param BatchEngineConfig config: The configuration for the batch engine
        :param Optional[AbstractRunStorage] storage: The storage to store execution results
        :param Optional[Executor] executor: The executor to run the flow (if needed)
        """

        self._func: Callable = func
        self._config: BatchEngineConfig = config
        self._storage: AbstractRunStorage = storage or NoOpRunStorage()

        self._batch_timeout_sec = self._config.batch_timeout_seconds
        self._line_timeout_sec = self._config.line_timeout_seconds
        self._max_worker_count = self._config.max_concurrency

        self._executor: Optional[Executor] = executor
        self._is_canceled: bool = False

    async def run(
        self,
        data: Sequence[Mapping[str, Any]],
        column_mapping: Optional[Mapping[str, str]],
        *,
        id: Optional[str] = None,
        max_lines: Optional[int] = None,
    ) -> BatchResult:
        if not data:
            raise BatchEngineValidationError("Please provide a non-empty data mapping.")

        start_time = datetime.now(timezone.utc)

        batch_inputs = self._apply_column_mapping(data, column_mapping, max_lines)
        if not batch_inputs or all(len(data) == 0 for data in batch_inputs):
            raise BatchEngineValidationError("No data to process.")

        try:
            id = id or str(uuid4())
            result: BatchResult = await self._exec_in_task(id, batch_inputs, start_time)
            return result
        except EvaluationException:
            raise
        except Exception as ex:
            raise BatchEngineError(
                "Unexpected error while running the batch run.", blame=ErrorBlame.SYSTEM_ERROR
            ) from ex

    def cancel(self):
        # TODO ralphe: Make sure this works
        self._is_canceled = True

    def _apply_column_mapping(
        self,
        data: Sequence[Mapping[str, Any]],
        column_mapping: Optional[Mapping[str, str]],
        max_lines: Optional[int],
    ) -> Sequence[Mapping[str, str]]:

        resolved_column_mapping: Mapping[str, str] = self._resolve_column_mapping(column_mapping)
        resolved_column_mapping.update(self._generate_defaults_for_column_mapping())
        return self._apply_column_mapping_to_lines(data, resolved_column_mapping, max_lines)

    def _resolve_column_mapping(
        self,
        column_mapping: Optional[Mapping[str, str]],
    ) -> Mapping[str, str]:
        parameters = inspect.signature(self._func).parameters
        default_column_mapping: Dict[str, str] = {
            name: f"${{data.{name}}}"
            for name, value in parameters.items()
            if name not in ["self", "cls", "args", "kwargs"]
        }
        resolved_mapping: Dict[str, str] = default_column_mapping.copy()

        for name, value in parameters.items():
            if value and value.default is not inspect.Parameter.empty:
                resolved_mapping.pop(name)

        resolved_mapping.update(column_mapping or {})
        return resolved_mapping

    def _generate_defaults_for_column_mapping(self) -> Mapping[Literal["$defaults$"], Any]:

        return {
            DEFAULTS_KEY: {
                name: value.default
                for name, value in inspect.signature(self._func).parameters.items()
                if value.default is not inspect.Parameter.empty
            }
        }

    @staticmethod
    def _apply_column_mapping_to_lines(
        data: Sequence[Mapping[str, Any]],
        column_mapping: Mapping[str, str],
        max_lines: Optional[int],
    ) -> Sequence[Mapping[str, Any]]:
        data = data[:max_lines] if max_lines else data

        inputs: Sequence[Mapping[str, Any]] = []
        defaults = cast(Mapping[str, Any], column_mapping.get(DEFAULTS_KEY, {}))

        for line_number, input in enumerate(data, start=1):
            mapped: Dict[str, Any] = {}
            missing_inputs: Set[str] = set()

            for key, value in column_mapping.items():
                if key == DEFAULTS_KEY:
                    # Skip the defaults key
                    continue

                if not isinstance(value, str):
                    # All non-string values are literal values.
                    mapped[key] = value
                    continue

                match: Optional[re.Match[str]] = re.search(KEYWORD_PATTERN, value)
                if match is None:
                    # Literal string value value
                    mapped[key] = value
                    continue

                dict_path = match.group(1)
                found, mapped_value = get_value_from_path(dict_path, input)
                if not found:  # try default value
                    found, mapped_value = get_value_from_path(dict_path, defaults)

                if found:
                    mapped[key] = mapped_value
                else:
                    missing_inputs.add(dict_path)

            if missing_inputs:
                missing = ", ".join(missing_inputs)
                raise BatchEngineValidationError(f"Missing inputs for line {line_number}: '{missing}'")

            inputs.append(mapped)

        return inputs

    async def _exec_in_task(
        self, run_id: str, batch_inputs: Sequence[Mapping[str, Any]], start_time: datetime
    ) -> BatchResult:
        # Since the batch execution is not guaranteed to be completed in the same order
        # as the inputs, we keep track of these in a mapping from index to result
        results: Dict[int, BatchRunDetails] = {}
        status: BatchStatus = BatchStatus.Completed
        error: Optional[Exception] = None

        task = asyncio.create_task(self._exec_batch(run_id, batch_inputs, start_time, results))

        while not task.done():
            # check whether the task is completed or canceled every 1s
            await asyncio.sleep(1)
            if self._is_canceled:
                task.cancel()
                # use current completed line results and aggregation results to create a BatchResult
                status = BatchStatus.Canceled
                error = BatchEngineCanceledError("The batch run is canceled by user.")
                break
            elif self._batch_timeout_expired(start_time):
                task.cancel()
                status = BatchStatus.Failed
                error = BatchEngineTimeoutError(
                    f"The batch run failed due to timeout [{self._batch_timeout_sec}s]. "
                    f"Please adjust the timeout to a higher value."
                )
                break

        end_time = datetime.now(timezone.utc)
        metrics = TokenMetrics(0, 0, 0)
        failed_lines: int = 0

        # generate the details in the same order as the inputs and fill in the missing results
        # with a failed status
        result_details = [
            (
                results[i]
                if i in results
                else BatchRunDetails(
                    id=BatchRunDetails.create_id(run_id, i),
                    status=BatchStatus.Failed,
                    result=None,
                    start_time=None,
                    end_time=None,
                    tokens=TokenMetrics(0, 0, 0),
                    error=BatchRunError("The line run is not completed.", None),
                    index=i,
                )
            )
            for i in range(len(batch_inputs))
        ]
        self.handle_line_failures(result_details)

        for line_result in result_details:
            # Indicate the worst status of the batch run. This works because
            # canceled and failed have a higher value than completed.
            status = max(status, line_result.status)
            if BatchStatus.is_failed(line_result.status):
                failed_lines += 1
            if line_result.tokens:
                metrics.prompt_tokens += line_result.tokens.prompt_tokens
                metrics.completion_tokens += line_result.tokens.completion_tokens
                metrics.total_tokens += line_result.tokens.total_tokens

        if failed_lines and not error:
            error_message = f"{floor(failed_lines / len(batch_inputs) * 100)}% of the batch run failed."
            first_exception: Optional[Exception] = next(
                (result.error.exception for result in result_details if result.error and result.error.exception),
                None,
            )
            if first_exception is not None:
                error_message += f" {first_exception}"

            error = BatchEngineRunFailedError(error_message)

        return BatchResult(
            status=status,
            total_lines=len(batch_inputs),
            failed_lines=failed_lines,
            start_time=start_time,
            end_time=end_time,
            tokens=metrics,
            details=result_details,
            error=error,
        )

    async def _exec_batch(
        self,
        run_id: str,
        batch_inputs: Sequence[Mapping[str, Any]],
        start_time: datetime,
        results: MutableMapping[int, BatchRunDetails],
    ) -> None:
        semaphore: Semaphore = Semaphore(self._max_worker_count)

        # TODO ralphe: This async code needs to refactored to use e.g. asyncio.gather, or
        #              asyncio.as_completed.
        # TODO ralphe: This code needs to handle cancellation better
        async def create_under_semaphore(index: int, inputs: Mapping[str, Any]):
            async with semaphore:
                return await self._exec_line_async(run_id, inputs, index)

        pending = [
            asyncio.create_task(create_under_semaphore(index, inputs)) for index, inputs in enumerate(batch_inputs)
        ]

        total_lines: int = len(batch_inputs)
        completed_lines: int = 0
        while completed_lines < total_lines:
            # TODO ralphe: Fix this code so it doesn't re-order the outputs
            # wait for any task to complete
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            completed_line_results = [task.result() for task in done]
            # persist node run infos and flow run info in line result to storage
            self._persist_run_info([result for _, result in completed_line_results])
            results.update({index: result for index, result in completed_line_results})
            # update the progress log
            completed_lines += len(completed_line_results)
            log_progress(
                run_start_time=start_time,
                total_count=total_lines,
                current_count=completed_lines,
                # TODO ralphe: set logger to use here
            )

    def __preprocess_inputs(self, inputs: Mapping[str, Any]) -> Mapping[str, Any]:

        func_params = inspect.signature(self._func).parameters

        has_kwargs = any(p.kind == p.VAR_KEYWORD for p in func_params.values())

        if has_kwargs:
            return inputs
        else:
            filtered_params = {key: value for key, value in inputs.items() if key in func_params}
            return filtered_params

    async def _exec_line_async(
        self,
        run_id: str,
        inputs: Mapping[str, Any],
        index: int,
    ) -> Tuple[int, BatchRunDetails]:
        with self._exec_line_context(run_id, index):
            details: BatchRunDetails = BatchRunDetails(
                id=f"{run_id}_{index}",
                status=BatchStatus.NotStarted,
                result=None,
                start_time=datetime.now(timezone.utc),
                end_time=None,
                tokens=TokenMetrics(0, 0, 0),
                error=None,
                index=index,
            )

            try:
                # TODO ralphe: Handle line timeouts here
                with CaptureOpenAITokenUsage() as captured_tokens:
                    # NOTE: In the legacy code, any synchronous functions were executed in a different process
                    #       for isolation reasons. However this isolation was violated in the way the code was
                    #       used by the evaluation SDK (e.g. you need to have the module already loaded to pass the
                    #       callable into the batch engine, so starting a new process to examine it was redundant).
                    #       It also came with performance and memory usage costs (each line was processed in a
                    #       separate process up to a maximum of 4), and these processes were created and torn down
                    #       too frequently.
                    #       For now we will just run the function in the current process, but in the future we may
                    #       want to consider running the function in a separate process for isolation reasons.
                    output: Any

                    processed_inputs = self.__preprocess_inputs(inputs)
                    if is_async_callable(self._func):
                        output = await self._func(**processed_inputs)
                    else:
                        # to maximize the parallelism, we run the synchronous function in a separate thread
                        # and await its result
                        output = await asyncio.get_event_loop().run_in_executor(
                            self._executor, partial(self._func, **processed_inputs)
                        )

                    # This should in theory never happen but as an extra precaution, let's check if the output
                    # is awaitable and await it if it is.
                    if inspect.isawaitable(output):
                        output = await output

                details.status = BatchStatus.Completed
                details.result = convert_eager_flow_output_to_dict(output)
                details.tokens.update(captured_tokens)
            except Exception as ex:
                details.status = BatchStatus.Failed
                details.error = BatchRunError(
                    f"Error while evaluating single input: {ex.__class__.__name__}: {str(ex)}", ex
                )
            finally:
                details.end_time = datetime.now(timezone.utc)

        return index, details

    @staticmethod
    def handle_line_failures(run_infos: List[BatchRunDetails], raise_on_line_failure: bool = False):
        """Handle line failures in batch run"""
        failed_run_infos: List[BatchRunDetails] = [r for r in run_infos if r.status == BatchStatus.Failed]
        failed_msg: Optional[str] = None
        if len(failed_run_infos) > 0:
            failed_indexes = ",".join([str(r.index) for r in failed_run_infos])
            first_fail_exception: str = failed_run_infos[0].error.details
            if raise_on_line_failure:
                failed_msg = "Flow run failed due to the error: " + first_fail_exception
                raise Exception(failed_msg)

            failed_msg = (
                f"{len(failed_run_infos)}/{len(run_infos)} flow run failed, indexes: [{failed_indexes}],"
                f" exception of index {failed_run_infos[0].index}: {first_fail_exception}"
            )
            logger.error(failed_msg)

    def _persist_run_info(self, line_results: Sequence[BatchRunDetails]):
        # TODO ralphe: implement?
        pass

    def _batch_timeout_expired(self, start_time: datetime) -> bool:
        if self._batch_timeout_sec is None:
            return False
        return (datetime.now(timezone.utc) - start_time).total_seconds() > self._batch_timeout_sec

    @contextmanager
    def _exec_line_context(self, run_id: str, line_number: int) -> Generator[None, Any, None]:
        # TODO ralphe: Do proper tracing and logging here
        log_manager = NodeLogManager()
        log_manager.set_node_context(run_id, "Flex", line_number)
        with log_manager, self._update_operation_context(run_id, line_number):
            yield

    @contextmanager
    def _update_operation_context(self, run_id: str, line_number: int) -> Generator[None, Any, None]:
        # operation_context = OperationContext.get_instance()
        # original_context = operation_context.copy()
        # original_mode = operation_context.get("run_mode", RunMode.Test.name)
        # values_for_context = {"flow_id": self._flow_id, "root_run_id": run_id}
        # if original_mode == RunMode.Batch.name:
        #     values_for_otel = {
        #         "batch_run_id": run_id,
        #         "line_number": line_number,
        #     }
        # else:
        #     values_for_otel = {"line_run_id": run_id}
        # try:
        #     append_promptflow_package_ua(operation_context)
        #     operation_context.set_execution_target(execution_target=self._execution_target)
        #     operation_context.set_default_tracing_keys(DEFAULT_TRACING_KEYS)
        #     operation_context.run_mode = original_mode
        #     operation_context.update(values_for_context)
        #     for k, v in values_for_otel.items():
        #         operation_context._add_otel_attributes(k, v)
        #     # Inject OpenAI API to make sure traces and headers injection works and
        #     # update OpenAI API configs from environment variables.
        #     inject_openai_api()
        yield

        # finally:
        #     OperationContext.set_instance(original_context)
