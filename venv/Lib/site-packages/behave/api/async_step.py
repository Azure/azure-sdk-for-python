# -*- coding: UTF-8 -*-
# pylint: disable=line-too-long
"""
This module provides functionality to support "async steps" (coroutines)
in a step-module with behave. This functionality simplifies to test
frameworks and protocols that make use of `asyncio.coroutines`_ or
provide `asyncio.coroutines`_.

EXAMPLE:

.. code-block:: python

    # -- FILE: features/steps/my_async_steps.py
    # EXAMPLE REQUIRES: Python >= 3.5
    from behave import step
    from behave.api.async_step import async_run_until_complete

    @step('an async coroutine step waits {duration:f} seconds')
    @async_run_until_complete
    async def step_async_step_waits_seconds(context, duration):
        await asyncio.sleep(duration)

.. code-block:: python

    # -- FILE: features/steps/my_async_steps2.py
    # EXAMPLE REQUIRES: Python >= 3.4
    from behave import step
    from behave.api.async_step import async_run_until_complete
    import asyncio

    @step('a tagged-coroutine async step waits {duration:f} seconds')
    @async_run_until_complete
    @asyncio.coroutine
    def step_async_step_waits_seconds2(context, duration):
        yield from asyncio.sleep(duration)


.. requires:: Python 3.5 (or 3.4) or :mod:`asyncio` backport (like :pypi:`trollius`)
.. seealso::
    https://docs.python.org/3/library/asyncio.html

.. _asyncio.coroutines: https://docs.python.org/3/library/asyncio-task.html#coroutines
"""
# pylint: enable=line-too-long

from __future__ import print_function
# -- REQUIRES: Python >= 3.4
# MAYBE BACKPORT: trollius
import functools
from six import string_types
try:
    import asyncio
    has_asyncio = True
except ImportError:
    has_asyncio = False

# -----------------------------------------------------------------------------
# ASYNC STEP DECORATORS:
# -----------------------------------------------------------------------------
def async_run_until_complete(astep_func=None, loop=None, timeout=None,
                             async_context=None, should_close=False):
    """Provides a function decorator for async-steps (coroutines).
    Provides an async event loop and runs the async-step until completion
    (or timeout, if specified).

    .. code-block:: python

        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step("an async step is executed")
        @async_run_until_complete
        async def astep_impl(context)
            await asycio.sleep(0.1)

        @step("an async step is executed")
        @async_run_until_complete(timeout=1.2)
        async def astep_impl2(context)
            # -- NOTE: Wrapped event loop waits with timeout=1.2 seconds.
            await asycio.sleep(0.3)

    Parameters:
        astep_func: Async step function (coroutine)
        loop (asyncio.EventLoop):   Event loop to use or None.
        timeout (int, float):       Timeout to wait for async-step completion.
        async_context (name):       Async_context name or object to use.
        should_close (bool):        Indicates if event lopp should be closed.

    .. note::

        * If :param:`loop` is None, the default event loop will be used
          or a new event loop is created.
        * If :param:`timeout` is provided, the event loop waits only the
          specified time.
        * :param:`async_context` is only used, if :param:`loop` is None.
        * If :param:`async_context` is a name, it will be used to retrieve
          the real async_context object from the context.

    """
    @functools.wraps(astep_func)
    def step_decorator(astep_func, context, *args, **kwargs):
        loop = kwargs.pop("_loop", None)
        timeout = kwargs.pop("_timeout", None)
        async_context = kwargs.pop("_async_context", None)
        should_close = kwargs.pop("_should_close", None)

        if isinstance(loop, string_types):
            loop = getattr(context, loop, None)
        elif async_context:
            if isinstance(async_context, string_types):
                name = async_context
                async_context = use_or_create_async_context(context, name)
                loop = async_context.loop
            else:
                assert isinstance(async_context, AsyncContext)
                loop = async_context.loop
        if loop is None:
            loop = asyncio.get_event_loop() or asyncio.new_event_loop()

        # -- WORKHORSE:
        try:
            if timeout is None:
                loop.run_until_complete(astep_func(context, *args, **kwargs))
            else:
                # MAYBE: loop = asyncio.new_event_loop()
                # MAYBE: should_close = True
                task = loop.create_task(astep_func(context, *args, **kwargs))
                done, pending = loop.run_until_complete(
                    asyncio.wait([task], timeout=timeout))
                assert not pending, "TIMEOUT-OCCURED: timeout=%s" % timeout
        finally:
            if loop and should_close:
                # -- MAYBE-AVOID:
                loop.close()

    if astep_func is None:
        # -- CASE: @decorator(timeout=1.2, ...)
        # MAYBE: return functools.partial(step_decorator,
        def wrapped_decorator1(astep_func):
            @functools.wraps(astep_func)
            def wrapped_decorator2(context, *args, **kwargs):
                return step_decorator(astep_func, context, *args,
                                      _loop=loop,
                                      _timeout=timeout,
                                      _async_context=async_context,
                                      _should_close=should_close, **kwargs)
            assert callable(astep_func)
            return wrapped_decorator2
        return wrapped_decorator1
    else:
        # -- CASE: @decorator ... or astep = decorator(astep)
        # MAYBE: return functools.partial(step_decorator, astep_func=astep_func)
        assert callable(astep_func)
        @functools.wraps(astep_func)
        def wrapped_decorator(context, *args, **kwargs):
            return step_decorator(astep_func, context, *args, **kwargs)
        return wrapped_decorator

# -- ALIAS:
run_until_complete = async_run_until_complete

# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY CLASSES:
# -----------------------------------------------------------------------------
class AsyncContext(object):
    # pylint: disable=line-too-long
    """Provides a context object for "async steps" to keep track:

    * which event loop is used
    * which (asyncio) tasks are used or of interest

    .. attribute:: loop
        Event loop object to use.
        If none is provided, the current event-loop is used
        (or a new one is created).

    .. attribute:: tasks
        List of started :mod:`asyncio` tasks (of interest).

    .. attribute:: name

        Optional name of this object (in the behave context).
        If none is provided, :attr:`AsyncContext.default_name` is used.

    .. attribute:: should_close
        Indicates if the :attr:`loop` (event-loop) should be closed or not.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/my_async_steps.py
        # REQUIRES: Python 3.5
        from behave import given, when, then, step
        from behave.api.async_step import AsyncContext

        @when('I dispatch an async-call with param "{param}"')
        def step_impl(context, param):
            async_context = getattr(context, "async_context", None)
            if async_context is None:
                async_context = context.async_context = AsyncContext()
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        @then('I wait at most {duration:f} seconds until all async-calls are completed')
        def step_impl(context, duration):
            async_context = context.async_context
            assert async_context.tasks
            done, pending = async_context.loop.run_until_complete(asyncio.wait(
                async_context.tasks, loop=async_context.loop, timeout=duration))
            assert len(pending) == 0

        # -- COROUTINE:
        async def my_async_func(param):
            await asyncio.sleep(0.5)
            return param.upper()
    """
    # pylint: enable=line-too-long
    default_name = "async_context"

    def __init__(self, loop=None, name=None, should_close=False, tasks=None):
        self.loop = loop or asyncio.get_event_loop() or asyncio.new_event_loop()
        self.tasks = tasks or []
        self.name = name or self.default_name
        self.should_close = should_close

    def __del__(self):
        if self.loop and self.should_close:
            self.close()

    def close(self):
        if self.loop and not self.loop.is_closed():
            self.loop.close()
            self.loop = None


# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def use_or_create_async_context(context, name=None, loop=None, **kwargs):
    """Utility function to be used in step implementations to ensure that an
    :class:`AsyncContext` object is stored in the :param:`context` object.

    If no such attribute exists (under the given name),
    a new :class:`AsyncContext` object is created with the provided args.
    Otherwise, the existing context attribute is used.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/my_async_steps.py
        # EXAMPLE REQUIRES: Python 3.5
        from behave import when
        from behave.api.async_step import use_or_create_async_context

        @when('I dispatch an async-call with param "{param}"')
        def step_impl(context, param):
            async_context = use_or_create_async_context(context, "async_context")
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        # -- COROUTINE:
        async def my_async_func(param):
            await asyncio.sleep(0.5)
            return param.upper()

    :param context:     Behave context object to use.
    :param name:        Optional name of async-context object (as string or None).
    :param loop:        Optional event_loop object to use for create call.
    :param kwargs:      Optional :class:`AsyncContext` params for create call.
    :return: :class:`AsyncContext` object from the param:`context`.
    """
    if name is None:
        name = AsyncContext.default_name
    async_context = getattr(context, name, None)
    if async_context is None:
        async_context = AsyncContext(loop=loop, name=name, **kwargs)
        setattr(context, async_context.name, async_context)
    assert isinstance(async_context, AsyncContext)
    assert getattr(context, async_context.name) is async_context
    return async_context
