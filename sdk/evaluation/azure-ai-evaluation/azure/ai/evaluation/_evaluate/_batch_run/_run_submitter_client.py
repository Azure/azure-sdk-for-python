# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import logging
import pandas as pd
import sys
import itertools
from collections import defaultdict
from concurrent.futures import Future
from os import PathLike
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
    cast,
)

from .batch_clients import BatchClientRun, HasAsyncCallable
from ..._legacy._batch_engine._run_submitter import RunSubmitter
from ..._legacy._batch_engine._config import BatchEngineConfig
from ..._legacy._batch_engine._run import Run
from ..._legacy._adapters._constants import LINE_NUMBER
from ..._legacy._adapters.types import AttrDict
from ..._legacy._common._thread_pool_executor_with_context import (
    ThreadPoolExecutorWithContext,
)
from ..._evaluate._utils import _has_aggregator
from ..._constants import Prefixes, PF_BATCH_TIMEOUT_SEC

from .._utils import get_int_env_var as get_int


LOGGER = logging.getLogger("run")
MISSING_VALUE: Final[int] = sys.maxsize


class RunSubmitterClient:
    def __init__(
        self,
        *,
        raise_on_errors: bool = False,
        config: Optional[BatchEngineConfig] = None,
    ) -> None:
        if config:
            self._config = config
        else:
            # Generate default config and apply any overrides to the configuration from environment variables
            self._config = BatchEngineConfig(LOGGER, use_async=True)
            if (val := get_int(PF_BATCH_TIMEOUT_SEC, MISSING_VALUE)) != MISSING_VALUE:
                self._config.batch_timeout_seconds = val
            if (val := get_int("PF_LINE_TIMEOUT_SEC", MISSING_VALUE)) != MISSING_VALUE:
                self._config.line_timeout_seconds = val
            if (val := get_int("PF_WORKER_COUNT", MISSING_VALUE)) != MISSING_VALUE:
                self._config.max_concurrency = val

        self._config.raise_on_error = raise_on_errors

        self._thread_pool = ThreadPoolExecutorWithContext(
            thread_name_prefix="evaluators_thread",
            max_workers=self._config.max_concurrency,
        )

    def run(
        self,
        flow: Callable,
        data: Union[str, PathLike, pd.DataFrame],
        column_mapping: Optional[Dict[str, str]] = None,
        evaluator_name: Optional[str] = None,
        **kwargs: Any,
    ) -> BatchClientRun:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")

        # The column mappings are indexed by data to indicate they come from the data
        # input. Update the inputs so that each entry is a dictionary with a data key
        # that contains the original input data.
        inputs = [{"data": input_data} for input_data in data.to_dict(orient="records")]
        # Pass the correct previous run to the evaluator
        run: Optional[BatchClientRun] = kwargs.pop("run", None)
        if run:
            kwargs["run"] = self._get_run(run)

        # Try to get async function to use
        if isinstance(flow, HasAsyncCallable):
            flow = flow._to_async()  # pylint: disable=protected-access

        # Start an event loop for async execution on a thread pool thread to separate it
        # from the caller's thread.
        run_submitter = RunSubmitter(self._config, self._thread_pool)
        run_future = self._thread_pool.submit(
            asyncio.run,
            run_submitter.submit(
                dynamic_callable=flow,
                inputs=inputs,
                column_mapping=column_mapping,
                name_prefix=evaluator_name,
                created_on=kwargs.pop("created_on", None),
                storage_creator=kwargs.pop("storage_creator", None),
                **kwargs,
            ),
        )

        return run_future

    def get_details(
        self, client_run: BatchClientRun, all_results: bool = False
    ) -> pd.DataFrame:
        run = self._get_run(client_run)

        def concat(*dataframes: pd.DataFrame) -> pd.DataFrame:
            return pd.concat(dataframes, axis=1, verify_integrity=True)

        def to_dataframe(
            items: Sequence[Mapping[str, Any]], *, max_length: Optional[int] = None
        ) -> pd.DataFrame:
            """Convert a sequence of dictionaries to a DataFrame.

            :param items: Sequence of dictionaries to convert.
            :type items: Sequence[Mapping[str, Any]]
            :param max_length: Maximum number of items to include in the DataFrame. If None, include all items.
            :type max_length: Optional[int]
            :return: DataFrame containing the items.
            :rtype: pd.DataFrame
            """
            max_length = None if all_results else self._config.default_num_results
            return pd.DataFrame(
                data=items if all_results else itertools.islice(items, max_length)
            )

        inputs = concat(
            to_dataframe(run.inputs),
            to_dataframe([{LINE_NUMBER: i} for i in range(len(run.inputs))]),
        ).add_prefix(Prefixes.INPUTS)

        outputs = to_dataframe(run.outputs).add_prefix(Prefixes.OUTPUTS)

        return concat(inputs, outputs)

    def get_metrics(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run = self._get_run(client_run)
        return {**run.metrics, **self._get_aggregated_metrics(client_run)}

    def _get_aggregated_metrics(self, client_run: BatchClientRun) -> Dict[str, Any]:
        aggregated_metrics = None
        run = self._get_run(client_run)
        try:
            if _has_aggregator(run.dynamic_callable):
                result_df = pd.DataFrame(run.outputs)
                if len(result_df.columns) == 1 and result_df.columns[0] == "output":
                    aggregate_input = result_df["output"].tolist()
                else:
                    aggregate_input = [
                        AttrDict(item) for item in result_df.to_dict("records")
                    ]

                aggr_func = getattr(run.dynamic_callable, "__aggregate__")
                aggregated_metrics = aggr_func(aggregate_input)

        except Exception as ex:  # pylint: disable=broad-exception-caught
            LOGGER.warning(
                "Error calculating aggregations for evaluator, failed with error %s", ex
            )

        if not isinstance(aggregated_metrics, dict):
            LOGGER.warning(
                "Aggregated metrics for evaluator is not a dictionary will not be logged as metrics",
            )
            return {}

        return aggregated_metrics

    def get_run_summary(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run = self._get_run(client_run)

        total_lines = run.result.total_lines if run.result else 0
        failed_lines = run.result.failed_lines if run.result else 0

        return {
            "status": run.status.value,
            "duration": str(run.duration),
            "completed_lines": total_lines - failed_lines,
            "failed_lines": failed_lines,
            "log_path": None,
            "error_message": (
                f"({run.result.error.blame.value}) {run.result.error.message}"
                if run.result and run.result.error and run.result.error.blame
                else None
            ),
            "error_code": (
                f"{run.result.error.category.value}"
                if run.result and run.result.error and run.result.error.category
                else None
            ),
        }

    @staticmethod
    def _get_run(run: BatchClientRun) -> Run:
        return cast(Future[Run], run).result()
