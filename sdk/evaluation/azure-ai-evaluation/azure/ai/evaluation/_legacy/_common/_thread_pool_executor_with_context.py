# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import contextvars
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing_extensions import override

class ThreadPoolExecutorWithContext(ThreadPoolExecutor):
    """ThreadPoolExecutor that preserves context variables across threads."""
    @override
    def submit(self, fn, *args, **kwargs):
        context = contextvars.copy_context()
        return super().submit(context.run, partial(fn, *args, **kwargs))
