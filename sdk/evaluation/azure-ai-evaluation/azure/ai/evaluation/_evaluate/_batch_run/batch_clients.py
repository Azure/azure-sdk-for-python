# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pandas
from os import PathLike
from typing import Any, Awaitable, Callable, Dict, Optional, Protocol, Union, runtime_checkable


class BatchClientRun(Protocol):
    """The protocol for the batch client run."""

    pass


@runtime_checkable
class HasAsyncCallable(Protocol):
    """The protocol for an object that has an async callable."""

    def _to_async(self) -> Callable[[Any, Any], Awaitable[Any]]: ...


class BatchClient(Protocol):
    """The protocol for the batch client. This allows for running a flow on a data source
    and getting the details of the run."""

    def run(
        self,
        flow: Callable,
        data: Union[str, PathLike, pandas.DataFrame],
        column_mapping: Optional[Dict[str, str]] = None,
        evaluator_name: Optional[str] = None,
        **kwargs: Any,
    ) -> BatchClientRun:
        """Run the given flow on the data with the given column mapping.

        :param flow: The flow to run.
        :type flow: Union[Callable, HasAsyncCallable]
        :param data: The JSONL file containing the data to run the flow on,
                     or the loaded data
        :type data: Union[str, PathLike]
        :param column_mapping: The column mapping to use.
        :type column_mapping: Mapping[str, str]
        :param name: The name of the run.
        :type name: Optional[str]
        :param kwargs: Additional keyword arguments to pass to the flow.
        :return: The result of the batch client run.
        :rtype: BatchClientRun
        """
        ...

    def get_details(self, client_run: BatchClientRun, all_results: bool = False) -> pandas.DataFrame:
        """Get the details of the run.

        :param client_run: The run to get the details of.
        :type client_run: BatchClientRun
        :param all_results: Whether to get all results.
        :type all_results: bool
        :return: The details of the run.
        :rtype: pandas.DataFrame
        """
        ...

    def get_metrics(self, client_run: BatchClientRun) -> Dict[str, Any]:
        """Get the metrics of the run.

        :param client_run: The run to get the metrics of.
        :type client_run: BatchClientRun
        :return: The metrics of the run.
        :rtype: Mapping[str, Any]
        """
        ...

    def get_run_summary(self, client_run: BatchClientRun) -> Dict[str, Any]:
        """Get the summary of the run.

        :param client_run: The run to get the summary of.
        :type client_run: BatchClientRun
        :return: The summary of the run.
        :rtype: Mapping[str, Any]
        """
        ...
