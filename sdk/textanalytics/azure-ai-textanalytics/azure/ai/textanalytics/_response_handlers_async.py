# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


import functools
from urllib.parse import urlparse, parse_qsl

from azure.core.async_paging import AsyncList
from ._models import RequestStatistics
from ._async_paging import (
    AnalyzeHealthcareEntitiesResultAsync,
    AnalyzeResultAsync
)
from ._response_handlers import healthcare_result, get_iter_items


async def healthcare_extract_page_data_async(doc_id_order, obj, response_headers, health_job_state): # pylint: disable=unused-argument
    return (health_job_state.next_link,
        healthcare_result(doc_id_order, health_job_state.results, response_headers, lro=True))


async def lro_get_next_page_async(lro_status_callback, first_page, continuation_token, show_stats=False):
    if continuation_token is None:
        return first_page

    try:
        continuation_token = continuation_token.decode("utf-8")

    except AttributeError:
        pass

    parsed_url = urlparse(continuation_token)
    job_id = parsed_url.path.split("/")[-1]
    query_params = dict(parse_qsl(parsed_url.query.replace("$", "")))
    query_params["show_stats"] = show_stats

    return await lro_status_callback(job_id, **query_params)


def healthcare_paged_result(doc_id_order, health_status_callback, response, obj, response_headers, show_stats=False): # pylint: disable=unused-argument
    return AnalyzeHealthcareEntitiesResultAsync(
        functools.partial(lro_get_next_page_async, health_status_callback, obj, show_stats=show_stats),
        functools.partial(healthcare_extract_page_data_async, doc_id_order, obj, response_headers),
        model_version=obj.results.model_version,
        statistics=RequestStatistics._from_generated(obj.results.statistics) if show_stats else None # pylint: disable=protected-access
    )

async def analyze_extract_page_data_async(doc_id_order, task_order, response_headers, analyze_job_state):
    iter_items = get_iter_items(doc_id_order, task_order, response_headers, analyze_job_state)
    return analyze_job_state.next_link, AsyncList(iter_items)

def analyze_paged_result(
    doc_id_order, task_order, analyze_status_callback, response, obj, response_headers, show_stats=False # pylint: disable=unused-argument
):
    return AnalyzeResultAsync(
        functools.partial(lro_get_next_page_async, analyze_status_callback, obj),
        functools.partial(analyze_extract_page_data_async, doc_id_order, task_order, response_headers),
    )
