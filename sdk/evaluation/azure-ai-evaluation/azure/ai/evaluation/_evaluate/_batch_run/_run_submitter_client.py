# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import logging
import pandas as pd
import sys
from collections import defaultdict
from concurrent.futures import Future
from os import PathLike
from typing import Any, Callable, Dict, Final, List, Mapping, Optional, Sequence, Union, cast

from .batch_clients import BatchClientRun, HasAsyncCallable
from ..._legacy._batch_engine._run_submitter import RunSubmitter
from ..._legacy._batch_engine._config import BatchEngineConfig
from ..._legacy._batch_engine._run import Run
from ..._legacy._adapters._constants import LINE_NUMBER
from ..._legacy._common._thread_pool_executor_with_context import ThreadPoolExecutorWithContext


LOGGER = logging.getLogger(__name__)


class RunSubmitterClient:
    def __init__(self, config: Optional[BatchEngineConfig] = None) -> None:
        self._config = config or BatchEngineConfig(LOGGER, use_async=True)
        self._thread_pool = ThreadPoolExecutorWithContext(
            thread_name_prefix="evaluators_thread",
            max_workers=self._config.max_concurrency)

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
            )
        )

        return run_future

    def get_details(self, client_run: BatchClientRun, all_results: bool = False) -> pd.DataFrame:
        run = self._get_run(client_run)

        data: Dict[str, List[Any]] = defaultdict(list)
        stop_at: Final[int] = self._config.default_num_results if not all_results else sys.maxsize

        def _update(prefix: str, items: Sequence[Mapping[str, Any]]) -> None:
            for i, line in enumerate(items):
                if i >= stop_at:
                    break
                for k, value in line.items():
                    key = f"{prefix}.{k}"
                    data[key].append(value)

        # Go from a list of dictionaries (i.e. a row view of the data) to a dictionary of lists
        # (i.e. a column view of the data)
        _update("inputs", run.inputs)
        _update("inputs", [{ LINE_NUMBER: i } for i in range(len(run.inputs)) ])
        _update("outputs", run.outputs)

        df = pd.DataFrame(data).reindex(columns=[k for k in data.keys()])
        return df

    def get_metrics(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run = self._get_run(client_run)
        return dict(run.metrics)

    def get_run_summary(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run = self._get_run(client_run)

        total_lines = run.result.total_lines if run.result else 0
        failed_lines = run.result.failed_lines if run.result else 0

        return {
            "status": run.status.value,
            "duration": str(run.duration),
            "completed_lines": total_lines - failed_lines,
            "failed_lines": failed_lines,
            # "log_path": "",
        }

    @staticmethod
    def _get_run(run: BatchClientRun) -> Run:
        return cast(Future[Run], run).result()
