# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import Any, Callable, Dict, Optional, Union
from typing_extensions import TypeAlias

import pandas as pd

from ._errors import MissingRequiredPackage
from ._configuration import Configuration
from .entities import Run


try:
    from promptflow.client import PFClient as _PFClient
except ImportError:

    class _PFClient:
        def __init__(self, **kwargs):
            self._config = Configuration(override_config=kwargs.pop("config", None))

        def run(
            self,
            flow: Union[str, PathLike, Callable],
            *,
            data: Union[str, PathLike],
            run: Optional[Union[str, Run]] = None,
            column_mapping: Optional[dict] = None,
            variant: Optional[str] = None,
            connections: Optional[dict] = None,
            environment_variables: Optional[dict] = None,
            name: Optional[str] = None,
            display_name: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None,
            resume_from: Optional[Union[str, Run]] = None,
            code: Optional[Union[str, PathLike]] = None,
            init: Optional[dict] = None,
            **kwargs,
        ) -> Run:
            raise MissingRequiredPackage("Please install 'promptflow' package to use PFClient")

        def get_details(self, run: Union[str, Run], max_results: int = 100, all_results: bool = False) -> pd.DataFrame:
            return pd.DataFrame()

        def get_metrics(self, run: Union[str, Run]) -> Dict[str, Any]:
            return {}


PFClient: TypeAlias = _PFClient
