# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, Dict, Final, Optional
from typing_extensions import TypeAlias


try:
    from promptflow.tracing import ThreadPoolExecutorWithContext as _ThreadPoolExecutorWithContext
    from promptflow.tracing._integrations._openai_injector import (
        inject_openai_api as _inject,
        recover_openai_api as _recover,
    )
    from promptflow.tracing import _start_trace
except ImportError:
    from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutorWithContext
    from azure.ai.evaluation._legacy._batch_engine._openai_injector import (
        inject_openai_api as _inject,
        recover_openai_api as _recover,
    )
    from azure.ai.evaluation._legacy._batch_engine._trace import start_trace as _start_trace


ThreadPoolExecutorWithContext: TypeAlias = _ThreadPoolExecutorWithContext
inject_openai_api: Final[Callable[[], None]] = _inject
recover_openai_api: Final[Callable[[], None]] = _recover
start_trace: Final = _start_trace
