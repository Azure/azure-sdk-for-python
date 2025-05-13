# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import inspect
import logging
import math
import os
from datetime import datetime
from collections import OrderedDict
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional, Union, cast

from azure.ai.evaluation._legacy._adapters.entities import Run
from azure.ai.evaluation._legacy._adapters._configuration import Configuration
from azure.ai.evaluation._legacy._adapters.client import PFClient
from azure.ai.evaluation._legacy._adapters.tracing import ThreadPoolExecutorWithContext
import pandas as pd

from azure.ai.evaluation._evaluate._batch_run.batch_clients import BatchClientRun, HasAsyncCallable


Configuration.get_instance().set_config("trace.destination", "none")
LOGGER = logging.getLogger(__name__)


class ProxyRun:
    def __init__(self, run: Future, **kwargs) -> None:  # pylint: disable=unused-argument
        self.run = run


class ProxyClient:  # pylint: disable=client-accepts-api-version-keyword
    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        **kwargs: Any,
    ) -> None:
        self._pf_client = PFClient(**kwargs)
        self._thread_pool = ThreadPoolExecutorWithContext(thread_name_prefix="evaluators_thread")

    def run(
        self,
        flow: Callable,
        data: Union[str, os.PathLike, pd.DataFrame],
        column_mapping: Optional[Dict[str, str]] = None,
        evaluator_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ProxyRun:
        if isinstance(data, pd.DataFrame):
            raise ValueError("Data cannot be a pandas DataFrame")

        flow_to_run: Callable = flow
        if os.getenv("AI_EVALS_BATCH_USE_ASYNC", "true").lower() == "true" and isinstance(flow, HasAsyncCallable):
            flow_to_run = flow._to_async()  # pylint: disable=protected-access

        name: str = kwargs.pop("name", "")
        if not name:
            name = f"azure_ai_evaluation_evaluators_{evaluator_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Pass the correct previous run to the evaluator
        run: Optional[BatchClientRun] = kwargs.pop("run", None)
        if run:
            kwargs["run"] = self.get_result(run)

        batch_use_async = self._should_batch_use_async(flow_to_run)
        eval_future = self._thread_pool.submit(
            self._pf_client.run,
            flow_to_run,
            data=data,
            column_mapping=column_mapping,  # type: ignore
            batch_use_async=batch_use_async,
            name=name,
            **kwargs,
        )
        return ProxyRun(run=eval_future)

    def get_details(self, client_run: BatchClientRun, all_results: bool = False) -> pd.DataFrame:
        run: Run = self.get_result(client_run)
        result_df = self._pf_client.get_details(run, all_results=all_results)
        result_df.replace("(Failed)", math.nan, inplace=True)
        return result_df

    def get_metrics(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run: Run = self.get_result(client_run)
        return self._pf_client.get_metrics(run)

    def get_run_summary(self, client_run: BatchClientRun) -> Dict[str, Any]:
        run: Run = self.get_result(client_run)

        # pylint: disable=protected-access
        completed_lines = run._properties.get("system_metrics", {}).get("__pf__.lines.completed", "NA")
        failed_lines = run._properties.get("system_metrics", {}).get("__pf__.lines.failed", "NA")

        # Update status to "Completed with Errors" if the original status is "Completed" and there are failed lines
        if run.status == "Completed" and failed_lines != "NA" and int(failed_lines) > 0:
            status = "Completed with Errors"
        else:
            status = run.status

        # Return the ordered dictionary with the updated status
        return OrderedDict(
            [
                ("status", status),
                ("duration", str((run._end_time or run._created_on) - run._created_on)),
                ("completed_lines", completed_lines),
                ("failed_lines", failed_lines),
                ("log_path", str(run._output_path)),
            ]
        )

    @staticmethod
    def get_result(run: BatchClientRun) -> Run:
        return cast(ProxyRun, run).run.result()

    @staticmethod
    def _should_batch_use_async(flow):
        if os.getenv("AI_EVALS_BATCH_USE_ASYNC", "true").lower() == "true":
            if hasattr(flow, "__call__") and inspect.iscoroutinefunction(flow.__call__):
                return True
            if inspect.iscoroutinefunction(flow):
                return True
            return False
        return False
