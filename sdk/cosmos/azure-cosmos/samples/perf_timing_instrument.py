"""Monkey-patch timing instrumentation into the async query path.

Standalone version — works with any azure-cosmos version.
Import this module before running the benchmark to add timing.
"""
import time
import perf_timing
from azure.cosmos.aio import _asynchronous_request, _retry_utility_async
from azure.cosmos._execution_context.aio import base_execution_context
from azure.cosmos import _base

# 1. Instrument ExecuteAsync
_orig_execute_async = _retry_utility_async.ExecuteAsync

async def _timed_execute_async(client, global_endpoint_manager, function, *args, **kwargs):
    t0 = time.perf_counter()
    result = await _orig_execute_async(client, global_endpoint_manager, function, *args, **kwargs)
    perf_timing.record("ExecuteAsync (retry wrapper)", time.perf_counter() - t0)
    return result

_retry_utility_async.ExecuteAsync = _timed_execute_async


# 2. Instrument AsynchronousRequest
_orig_async_request = _asynchronous_request.AsynchronousRequest

async def _timed_async_request(client, request_params, global_endpoint_manager,
                                connection_policy, pipeline_client, request, request_data, **kwargs):
    t0 = time.perf_counter()
    result = await _orig_async_request(client, request_params, global_endpoint_manager,
                                        connection_policy, pipeline_client, request, request_data, **kwargs)
    perf_timing.record("AsynchronousRequest (total)", time.perf_counter() - t0)
    return result

_asynchronous_request.AsynchronousRequest = _timed_async_request


# 3. Instrument _PipelineRunFunction
_orig_pipeline_run = _asynchronous_request._PipelineRunFunction

async def _timed_pipeline_run(pipeline_client, request, **kwargs):
    t0 = time.perf_counter()
    result = await _orig_pipeline_run(pipeline_client, request, **kwargs)
    perf_timing.record("PipelineRunFunction (HTTP+policies)", time.perf_counter() - t0)
    return result

_asynchronous_request._PipelineRunFunction = _timed_pipeline_run


# 4. Instrument _fetch_items_helper_no_retries
_orig_fetch_no_retries = base_execution_context._QueryExecutionContextBase._fetch_items_helper_no_retries

async def _timed_fetch_no_retries(self, fetch_function):
    t0 = time.perf_counter()
    result = await _orig_fetch_no_retries(self, fetch_function)
    perf_timing.record("fetch_items_no_retries", time.perf_counter() - t0)
    return result

base_execution_context._QueryExecutionContextBase._fetch_items_helper_no_retries = _timed_fetch_no_retries


# 5. Instrument GetHeaders
_orig_get_headers = _base.GetHeaders

def _timed_get_headers(*args, **kwargs):
    t0 = time.perf_counter()
    result = _orig_get_headers(*args, **kwargs)
    perf_timing.record("GetHeaders", time.perf_counter() - t0)
    return result

_base.GetHeaders = _timed_get_headers

print("[TIMING] Instrumentation installed.")
