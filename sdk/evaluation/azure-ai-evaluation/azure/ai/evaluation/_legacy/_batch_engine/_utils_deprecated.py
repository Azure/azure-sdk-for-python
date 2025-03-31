# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import contextvars
import dataclasses
from asyncio import Task
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterator, Callable, Iterator, Mapping, Optional, Sequence, Tuple, cast


class ThreadPoolExecutorWithContext(ThreadPoolExecutor):
    # Original source:
    # promptflow-tracing/promptflow/tracing/_context_utils.py

    def __init__(
        self,
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "",
        initializer: Optional[Callable] = None,
        initargs: Tuple[Any, ...] = (),
    ) -> None:
        """The ThreadPoolExecutionWithContext is an extended thread pool implementation
        which will copy the context from the current thread to the child threads.
        Thus the traced functions in child threads could keep parent-child relationship in the tracing system.
        The arguments are the same as ThreadPoolExecutor.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.
        """
        current_context = contextvars.copy_context()
        initializer_args = (current_context, initializer, initargs)
        super().__init__(max_workers, thread_name_prefix, self.set_context_then_call, initializer_args)

    @staticmethod
    def set_context_then_call(
        context: contextvars.Context,
        initializer: Optional[Callable],
        initargs: Tuple[Any, ...],
    ) -> None:
        for var, value in context.items():
            var.set(value)
        if initializer:
            initializer(*initargs)


def _has_running_loop() -> bool:
    """Check if the current thread has a running event loop."""
    # When using asyncio.get_running_loop(), a RuntimeError is raised if there is no running event loop.
    # So, we use a try-catch block to determine whether there is currently an event loop in place.
    #
    # Note that this is the only way to check whether there is a running loop now, see:
    # https://docs.python.org/3/library/asyncio-eventloop.html?highlight=get_running_loop#asyncio.get_running_loop
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def async_run_allowing_running_loop(async_func, *args, **kwargs):
    """Run an async function in a new thread, allowing the current thread to have a running event loop.

    When run in an async environment (e.g., in a notebook), because each thread allows only one event
    loop, using asyncio.run directly leads to a RuntimeError ("asyncio.run() cannot be called from a
    running event loop").

    To address this issue, we add a check for the event loop here. If the current thread already has an
    event loop, we run _exec_batch in a new thread; otherwise, we run it in the current thread.
    """

    if _has_running_loop():
        # TODO ralphe: The logic here makes absolutely no sense to me. If you already have an
        #              async event loop running, why would you want to start up a new thread,
        #              create a new event loop, and run the async function in a new thread?
        #              You can just use the following to schedule the async function call on
        #              the existing event loop:
        # asyncio.get_running_loop().create_task(async_func(*args, *args, **kwargs)).result()
        #              The correct thing to do here is not make these decisions here at all.
        #              Instead, all the BatchEngine code should be async first, with the event
        #              loop being started by the callers of that code. For now, I am keeping
        #              this odd logic as is, and in phase 2 of the migration, this will be
        #              refactored to be more idiomatic asyncio code.
        with ThreadPoolExecutorWithContext() as executor:
            return executor.submit(lambda: asyncio.run(async_func(*args, **kwargs))).result()
    else:
        return asyncio.run(async_func(*args, **kwargs))


async def stringify_output_async(output: Any) -> str:
    if isinstance(output, AsyncIterator):
        return await stringify_output_async([v async for v in output])
    if isinstance(output, Iterator):
        return await stringify_output_async([v for v in output])
    if isinstance(output, Mapping):
        return ", ".join(
            [f"{await stringify_output_async(k)}:{await stringify_output_async(v)}" for k, v in output.items()]
        )
    if isinstance(output, Sequence):
        return "".join([await stringify_output_async(v) for v in output])
    if isinstance(output, Task):
        return await stringify_output_async(await output)

    return str(output)


def convert_eager_flow_output_to_dict(value: Any) -> Mapping[str, Any]:
    """
    Convert the output of eager flow to a dict. Since the output of eager flow
    may not be a dict, we need to convert it to a dict in batch mode.

    Examples:
    1. If the output is a dict, return it directly:
        value = {"output": 1} -> {"output": 1}
    2. If the output is a dataclass, convert it to a dict:
        value = SampleDataClass(output=1) -> {"output": 1}
    3. If the output is not a dict or dataclass, convert it to a dict by adding a key "output":
        value = 1 -> {"output": 1}
    """

    if isinstance(value, Mapping):
        return value
    elif dataclasses.is_dataclass(value):
        return dataclasses.asdict(cast(Any, value))
    else:
        return {"output": value}
