# Copyright 2018, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import threading
from multiprocessing import pool
from concurrent import futures

from opencensus.trace import execution_context
from opencensus.trace import tracer
from opencensus.trace.propagation import binary_format

log = logging.getLogger(__name__)

MODULE_NAME = "threading"


def trace_integration(tracer=None):
    """Wrap threading functions to trace."""
    log.info("Integrated module: {}".format(MODULE_NAME))
    # Wrap the threading start function
    start_func = getattr(threading.Thread, "start")
    setattr(
        threading.Thread, start_func.__name__, wrap_threading_start(start_func)
    )

    # Wrap the threading run function
    run_func = getattr(threading.Thread, "run")
    setattr(threading.Thread, run_func.__name__, wrap_threading_run(run_func))

    # Wrap the threading run function
    apply_async_func = getattr(pool.Pool, "apply_async")
    setattr(
        pool.Pool,
        apply_async_func.__name__,
        wrap_apply_async(apply_async_func),
    )

    # Wrap the threading run function
    submit_func = getattr(futures.ThreadPoolExecutor, "submit")
    setattr(
        futures.ThreadPoolExecutor,
        submit_func.__name__,
        wrap_submit(submit_func),
    )


def wrap_threading_start(start_func):
    """Wrap the start function from thread. Put the tracer informations in the
    threading object.
    """

    def call(self):
        self._opencensus_context = (
            execution_context.get_opencensus_full_context()
        )
        return start_func(self)

    return call


def wrap_threading_run(run_func):
    """Wrap the run function from thread. Get the tracer informations from the
    threading object and set it as current tracer.
    """

    def call(self):
        execution_context.set_opencensus_full_context(
            *self._opencensus_context
        )
        return run_func(self)

    return call


def wrap_apply_async(apply_async_func):
    """Wrap the apply_async function of multiprocessing.pools. Get the function
    that will be called and wrap it then add the opencensus context."""

    def call(self, func, args=(), kwds={}, **kwargs):
        wrapped_func = wrap_task_func(func)
        _tracer = execution_context.get_opencensus_tracer()
        propagator = binary_format.BinaryFormatPropagator()

        wrapped_kwargs = {}
        wrapped_kwargs["span_context_binary"] = propagator.to_header(
            _tracer.span_context
        )
        wrapped_kwargs["kwds"] = kwds
        wrapped_kwargs["sampler"] = _tracer.sampler
        wrapped_kwargs["exporter"] = _tracer.exporter
        wrapped_kwargs["propagator"] = _tracer.propagator

        return apply_async_func(
            self, wrapped_func, args=args, kwds=wrapped_kwargs, **kwargs
        )

    return call


def wrap_submit(submit_func):
    """Wrap the apply_async function of multiprocessing.pools. Get the function
    that will be called and wrap it then add the opencensus context."""

    def call(self, func, *args, **kwargs):
        wrapped_func = wrap_task_func(func)
        _tracer = execution_context.get_opencensus_tracer()
        propagator = binary_format.BinaryFormatPropagator()

        wrapped_kwargs = {}
        wrapped_kwargs["span_context_binary"] = propagator.to_header(
            _tracer.span_context
        )
        wrapped_kwargs["kwds"] = kwargs
        wrapped_kwargs["sampler"] = _tracer.sampler
        wrapped_kwargs["exporter"] = _tracer.exporter
        wrapped_kwargs["propagator"] = _tracer.propagator

        return submit_func(self, wrapped_func, *args, **wrapped_kwargs)

    return call


class wrap_task_func(object):
    """Wrap the function given to apply_async to get the tracer from context,
    execute the function then clear the context."""

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        kwds = kwargs.pop("kwds")

        span_context_binary = kwargs.pop("span_context_binary")
        propagator = binary_format.BinaryFormatPropagator()
        kwargs["span_context"] = propagator.from_header(span_context_binary)

        _tracer = tracer.Tracer(**kwargs)
        execution_context.set_opencensus_tracer(_tracer)
        with _tracer.span(name=threading.current_thread().name):
            result = self.func(*args, **kwds)
        execution_context.clean()
        return result
