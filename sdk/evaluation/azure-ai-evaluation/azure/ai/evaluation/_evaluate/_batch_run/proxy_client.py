# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import inspect
import logging
import math
import os
from collections import OrderedDict
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd
from promptflow.client import PFClient
from promptflow.entities import Run
from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor

LOGGER = logging.getLogger(__name__)


class ProxyRun:
    def __init__(self, run: Future, **kwargs) -> None:  # pylint: disable=unused-argument
        self.run = run


class ProxyClient:  # pylint: disable=client-accepts-api-version-keyword
    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
        self, pf_client: PFClient
    ) -> None:
        self._pf_client = pf_client
        self._thread_pool = ThreadPoolExecutor(thread_name_prefix="evaluators_thread")

    def run(
        self,
        flow: Union[str, os.PathLike, Callable],
        data: Union[str, os.PathLike],
        column_mapping: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ProxyRun:
        flow_to_run = flow
        if os.getenv("AI_EVALS_BATCH_USE_ASYNC", "true").lower() == "true" and hasattr(flow, "_to_async"):
            flow_to_run = flow._to_async()  # pylint: disable=protected-access

        batch_use_async = self._should_batch_use_async(flow_to_run)
        eval_future = self._thread_pool.submit(
            self._pf_client.run,
            flow_to_run,
            data=data,
            column_mapping=column_mapping,
            batch_use_async=batch_use_async,
            **kwargs
        )
        return ProxyRun(run=eval_future)

    def get_details(self, proxy_run: ProxyRun, all_results: bool = False) -> pd.DataFrame:
        run: Run = proxy_run.run.result()
        result_df = self._pf_client.get_details(run, all_results=all_results)
        result_df.replace("(Failed)", math.nan, inplace=True)
        return result_df

    def get_metrics(self, proxy_run: ProxyRun) -> Dict[str, Any]:
        run: Run = proxy_run.run.result()
        return self._pf_client.get_metrics(run)

    def get_run_summary(self, proxy_run: ProxyRun) -> Dict[str, Any]:
        run = proxy_run.run.result()

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
                ("duration", str(run._end_time - run._created_on)),
                ("completed_lines", completed_lines),
                ("failed_lines", failed_lines),
                ("log_path", str(run._output_path)),
            ]
        )

    @staticmethod
    def _should_batch_use_async(flow):
        if os.getenv("AI_EVALS_BATCH_USE_ASYNC", "true").lower() == "true":
            if hasattr(flow, "__call__") and inspect.iscoroutinefunction(flow.__call__):
                return True
            if inspect.iscoroutinefunction(flow):
                return True
            return False
        return False
