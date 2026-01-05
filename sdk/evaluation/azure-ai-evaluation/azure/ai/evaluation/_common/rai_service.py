# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import copy
import importlib.metadata
import logging
import math
import re
import time
import json
import html
from ast import literal_eval
from typing import Dict, List, Optional, Union, cast
from urllib.parse import urlparse
from string import Template
from azure.ai.evaluation._common.onedp._client import ProjectsClient as AIProjectClient
from azure.ai.evaluation._common.onedp.models import QueryResponseInlineMessage, EvaluatorMessage
from azure.ai.evaluation._common.onedp._utils.model_base import SdkJSONEncoder
from azure.core.exceptions import HttpResponseError

import jwt

from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import AsyncHttpPipeline, get_async_http_client, get_http_client
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._user_agent import UserAgentSingleton
from azure.ai.evaluation._common.utils import is_onedp_project
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import AsyncRetryPolicy, UserAgentPolicy

from .constants import (
    CommonConstants,
    EvaluationMetrics,
    RAIService,
    Tasks,
    _InternalEvaluationMetrics,
)
from .utils import get_harm_severity_level, retrieve_content_type


LOGGER = logging.getLogger(__name__)

USER_TEXT_TEMPLATE_DICT: Dict[str, Template] = {
    "DEFAULT": Template("<Human>{$query}</><System>{$response}</>"),
}
ML_WORKSPACE = "https://management.azure.com/.default"
COG_SRV_WORKSPACE = "https://ai.azure.com/.default"

INFERENCE_OF_SENSITIVE_ATTRIBUTES = "inference_sensitive_attributes"


def get_formatted_template(data: dict, annotation_task: str) -> str:
    """Given the task and input data, produce a formatted string that will serve as the main
    payload for the RAI service. Requires specific per-task logic.

    :param data: The data to incorporate into the payload.
    :type data: dict
    :param annotation_task: The annotation task to use. This determines the template to use.
    :type annotation_task: str
    :return: The formatted based on the data and task template.
    :rtype: str
    """
    # Template class doesn't play nice with json dumping/loading, just handle groundedness'
    # JSON format manually.
    # Template was: Template('{"question": "$query", "answer": "$response", "context": "$context"}'),
    if annotation_task == Tasks.GROUNDEDNESS:
        as_dict = {
            "question": data.get("query", ""),
            "answer": data.get("response", ""),
            "context": data.get("context", ""),
        }
        return json.dumps(as_dict)
    if annotation_task == Tasks.CODE_VULNERABILITY:
        as_dict = {"context": data.get("query", ""), "completion": data.get("response", "")}
        return json.dumps(as_dict)
    if annotation_task == Tasks.UNGROUNDED_ATTRIBUTES:
        as_dict = {
            "query": data.get("query", ""),
            "response": data.get("response", ""),
            "context": data.get("context", ""),
        }
        return json.dumps(as_dict)
    as_dict = {
        "query": html.escape(data.get("query", "")),
        "response": html.escape(data.get("response", "")),
    }
    user_text = USER_TEXT_TEMPLATE_DICT.get(annotation_task, USER_TEXT_TEMPLATE_DICT["DEFAULT"]).substitute(**as_dict)
    return user_text.replace("'", '\\"')


def get_common_headers(token: str, evaluator_name: Optional[str] = None) -> Dict:
    """Get common headers for the HTTP request

    :param token: The Azure authentication token.
    :type token: str
    :param evaluator_name: The evaluator name. Default is None.
    :type evaluator_name: str
    :return: The common headers.
    :rtype: Dict
    """
    user_agent = (
        f"{UserAgentSingleton().value} (type=evaluator; subtype={evaluator_name})"
        if evaluator_name
        else UserAgentSingleton().value
    )
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": user_agent,
    }


def get_async_http_client_with_timeout() -> AsyncHttpPipeline:
    return get_async_http_client().with_policies(
        retry_policy=AsyncRetryPolicy(timeout=CommonConstants.DEFAULT_HTTP_TIMEOUT)
    )


async def ensure_service_availability_onedp(
    client: AIProjectClient, token: str, capability: Optional[str] = None
) -> None:
    """Check if the Responsible AI service is available in the region and has the required capability, if relevant.

    :param client: The AI project client.
    :type client: AIProjectClient
    :param token: The Azure authentication token.
    :type token: str
    :param capability: The capability to check. Default is None.
    :type capability: str
    :raises Exception: If the service is not available in the region or the capability is not available.
    """
    headers = get_common_headers(token)
    capabilities = client.evaluations.check_annotation(headers=headers)

    if capability and capability not in capabilities:
        msg = f"The needed capability '{capability}' is not supported by the RAI service in this region."
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.RAI_CLIENT,
            category=ErrorCategory.SERVICE_UNAVAILABLE,
            blame=ErrorBlame.USER_ERROR,
            tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
        )


async def ensure_service_availability(rai_svc_url: str, token: str, capability: Optional[str] = None) -> None:
    """Check if the Responsible AI service is available in the region and has the required capability, if relevant.

    :param rai_svc_url: The Responsible AI service URL.
    :type rai_svc_url: str
    :param token: The Azure authentication token.
    :type token: str
    :param capability: The capability to check. Default is None.
    :type capability: str
    :raises Exception: If the service is not available in the region or the capability is not available.
    """
    headers = get_common_headers(token)
    svc_liveness_url = rai_svc_url + "/checkannotation"

    async with get_async_http_client() as client:
        response = await client.get(svc_liveness_url, headers=headers)

        if response.status_code != 200:
            msg = (
                f"RAI service is unavailable in this region, or you lack the necessary permissions "
                f"to access the AI project. Status Code: {response.status_code}"
            )
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.RAI_CLIENT,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                blame=ErrorBlame.USER_ERROR,
                tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
            )

        capabilities = response.json()
        if capability and capability not in capabilities:
            msg = f"The needed capability '{capability}' is not supported by the RAI service in this region."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.RAI_CLIENT,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                blame=ErrorBlame.USER_ERROR,
                tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
            )


def generate_payload(normalized_user_text: str, metric: str, annotation_task: str) -> Dict:
    """Generate the payload for the annotation request

    :param normalized_user_text: The normalized user text to be entered as the "UserTextList" in the payload.
    :type normalized_user_text: str
    :param metric: The evaluation metric to use. This determines the task type, and whether a "MetricList" is needed
        in the payload.
    :type metric: str
    :param annotation_task: The annotation task to be passed to service
    :type annotation_task: str
    :return: The payload for the annotation request.
    :rtype: Dict
    """
    include_metric = True
    task = annotation_task
    if metric == EvaluationMetrics.PROTECTED_MATERIAL:
        include_metric = False
    elif metric == EvaluationMetrics.UNGROUNDED_ATTRIBUTES:
        include_metric = False
    elif metric == _InternalEvaluationMetrics.ECI:
        include_metric = False
    elif metric == EvaluationMetrics.XPIA:
        include_metric = False
    return (
        {
            "UserTextList": [normalized_user_text],
            "AnnotationTask": task,
            "MetricList": [metric],
        }
        if include_metric
        else {
            "UserTextList": [normalized_user_text],
            "AnnotationTask": task,
        }
    )


async def submit_request(
    data: dict, metric: str, rai_svc_url: str, token: str, annotation_task: str, evaluator_name: str
) -> str:
    """Submit request to Responsible AI service for evaluation and return operation ID

    :param data: The data to evaluate.
    :type data: dict
    :param metric: The evaluation metric to use.
    :type metric: str
    :param rai_svc_url: The Responsible AI service URL.
    :type rai_svc_url: str
    :param token: The Azure authentication token.
    :type token: str
    :param annotation_task: The annotation task to use.
    :type annotation_task: str
    :param evaluator_name: The evaluator name.
    :type evaluator_name: str
    :return: The operation ID.
    :rtype: str
    """
    normalized_user_text = get_formatted_template(data, annotation_task)
    payload = generate_payload(normalized_user_text, metric, annotation_task=annotation_task)

    url = rai_svc_url + "/submitannotation"
    headers = get_common_headers(token, evaluator_name)

    async with get_async_http_client_with_timeout() as client:
        http_response = await client.post(url, json=payload, headers=headers)

    if http_response.status_code != 202:
        LOGGER.error("Fail evaluating '%s' with error message: %s", payload["UserTextList"], http_response.text())
        http_response.raise_for_status()
    result = http_response.json()
    operation_id = result["location"].split("/")[-1]
    return operation_id


async def submit_request_onedp(
    client: AIProjectClient,
    data: dict,
    metric: str,
    token: str,
    annotation_task: str,
    evaluator_name: str,
    scan_session_id: Optional[str] = None,
) -> str:
    """Submit request to Responsible AI service for evaluation and return operation ID

    :param client: The AI project client.
    :type client: AIProjectClient
    :param data: The data to evaluate.
    :type data: dict
    :param metric: The evaluation metric to use.
    :type metric: str
    :param token: The Azure authentication token.
    :type token: str
    :param annotation_task: The annotation task to use.
    :type annotation_task: str
    :param evaluator_name: The evaluator name.
    :type evaluator_name: str
    :param scan_session_id: The scan session ID to use for the evaluation.
    :type scan_session_id: Optional[str]
    :return: The operation ID.
    :rtype: str
    """
    normalized_user_text = get_formatted_template(data, annotation_task)
    payload = generate_payload(normalized_user_text, metric, annotation_task=annotation_task)
    headers = get_common_headers(token, evaluator_name)
    if scan_session_id:
        headers["x-ms-client-request-id"] = scan_session_id
    response = client.evaluations.submit_annotation(payload, headers=headers)
    result = json.loads(response)
    operation_id = result["location"].split("/")[-1]
    return operation_id


async def fetch_result(operation_id: str, rai_svc_url: str, credential: TokenCredential, token: str) -> Dict:
    """Fetch the annotation result from Responsible AI service

    :param operation_id: The operation ID.
    :type operation_id: str
    :param rai_svc_url: The Responsible AI service URL.
    :type rai_svc_url: str
    :param credential: The Azure authentication credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param token: The Azure authentication token.
    :type token: str
    :return: The annotation result.
    :rtype: Dict
    """
    start = time.time()
    request_count = 0

    url = rai_svc_url + "/operations/" + operation_id
    while True:
        token = await fetch_or_reuse_token(credential, token)
        headers = get_common_headers(token)

        async with get_async_http_client() as client:
            response = await client.get(url, headers=headers, timeout=RAIService.TIMEOUT)

        if response.status_code == 200:
            return response.json()

        request_count += 1
        time_elapsed = time.time() - start
        if time_elapsed > RAIService.TIMEOUT:
            raise TimeoutError(f"Fetching annotation result {request_count} times out after {time_elapsed:.2f} seconds")

        sleep_time = RAIService.SLEEP_TIME**request_count
        await asyncio.sleep(sleep_time)


async def fetch_result_onedp(client: AIProjectClient, operation_id: str, token: str) -> Dict:
    """Fetch the annotation result from Responsible AI service

    :param client: The AI project client.
    :type client: AIProjectClient
    :param operation_id: The operation ID.
    :type operation_id: str
    :param token: The Azure authentication token.
    :type token: str
    :return: The annotation result.
    :rtype: Dict
    """
    start = time.time()
    request_count = 0

    while True:
        headers = get_common_headers(token)
        try:
            return client.evaluations.operation_results(operation_id, headers=headers)
        except HttpResponseError:
            request_count += 1
            time_elapsed = time.time() - start
            if time_elapsed > RAIService.TIMEOUT:
                raise TimeoutError(
                    f"Fetching annotation result {request_count} times out after {time_elapsed:.2f} seconds"
                )

            sleep_time = RAIService.SLEEP_TIME**request_count
            await asyncio.sleep(sleep_time)


def parse_response(  # pylint: disable=too-many-branches,too-many-statements
    batch_response: List[Dict], metric_name: str, metric_display_name: Optional[str] = None
) -> Dict[str, Union[str, float]]:
    """Parse the annotation response from Responsible AI service for a content harm evaluation.

    :param batch_response: The annotation response from Responsible AI service.
    :type batch_response: List[Dict]
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param metric_display_name: The evaluation metric display name to use. If unset, use the metric_name.
    :type metric_display_name: Optional[str]
    :return: The parsed annotation result.
    :rtype: Dict[str, Union[str, float]]
    """
    if metric_display_name is None:
        metric_display_name = metric_name

    # non-numeric metrics
    if metric_name in {
        EvaluationMetrics.PROTECTED_MATERIAL,
        _InternalEvaluationMetrics.ECI,
        EvaluationMetrics.XPIA,
        EvaluationMetrics.CODE_VULNERABILITY,
        EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
    }:
        result = {}
        if not batch_response or len(batch_response[0]) == 0:
            return {}
        if (
            metric_name == EvaluationMetrics.UNGROUNDED_ATTRIBUTES
            and INFERENCE_OF_SENSITIVE_ATTRIBUTES in batch_response[0]
        ):
            batch_response[0] = {
                EvaluationMetrics.UNGROUNDED_ATTRIBUTES: batch_response[0][INFERENCE_OF_SENSITIVE_ATTRIBUTES]
            }
        if metric_name == EvaluationMetrics.PROTECTED_MATERIAL and metric_name not in batch_response[0]:
            pm_metric_names = {"artwork", "fictional_characters", "logos_and_brands"}
            for pm_metric_name in pm_metric_names:
                response = batch_response[0][pm_metric_name]
                response = response.replace("false", "False")
                response = response.replace("true", "True")
                parsed_response = literal_eval(response)
                result[pm_metric_name + "_label"] = parsed_response["label"] if "label" in parsed_response else math.nan
                result[pm_metric_name + "_reason"] = (
                    parsed_response["reasoning"] if "reasoning" in parsed_response else ""
                )
                result[pm_metric_name + "_total_tokens"] = (
                    parsed_response["totalTokenCount"] if "totalTokenCount" in parsed_response else ""
                )
                result[pm_metric_name + "_prompt_tokens"] = (
                    parsed_response["inputTokenCount"] if "inputTokenCount" in parsed_response else ""
                )
                result[pm_metric_name + "_completion_tokens"] = (
                    parsed_response["outputTokenCount"] if "outputTokenCount" in parsed_response else ""
                )
                result[pm_metric_name + "_finish_reason"] = (
                    parsed_response["finish_reason"] if "finish_reason" in parsed_response else ""
                )
                result[pm_metric_name + "_sample_input"] = (
                    parsed_response["sample_input"] if "sample_input" in parsed_response else ""
                )
                result[pm_metric_name + "_sample_output"] = (
                    parsed_response["sample_output"] if "sample_output" in parsed_response else ""
                )
                result[pm_metric_name + "_model"] = parsed_response["model"] if "model" in parsed_response else ""
            return result
        if metric_name not in batch_response[0]:
            return {}
        response = batch_response[0][metric_name]
        response = response.replace("false", "False")
        response = response.replace("true", "True")
        parsed_response = literal_eval(response)
        # Use label instead of score since these are assumed to be boolean results.
        # Use math.nan as null value since it's ignored by aggregations rather than treated as 0.
        result[metric_display_name + "_label"] = parsed_response["label"] if "label" in parsed_response else math.nan
        result[metric_display_name + "_reason"] = parsed_response["reasoning"] if "reasoning" in parsed_response else ""

        if metric_name == EvaluationMetrics.XPIA:
            # Add "manipulated_content", "intrusion" and "information_gathering" to the result
            # if present else set them to math.nan
            result[metric_display_name + "_manipulated_content"] = (
                parsed_response["manipulated_content"] if "manipulated_content" in parsed_response else math.nan
            )
            result[metric_display_name + "_intrusion"] = (
                parsed_response["intrusion"] if "intrusion" in parsed_response else math.nan
            )
            result[metric_display_name + "_information_gathering"] = (
                parsed_response["information_gathering"] if "information_gathering" in parsed_response else math.nan
            )
        if (
            metric_name == EvaluationMetrics.CODE_VULNERABILITY
            or metric_name == EvaluationMetrics.UNGROUNDED_ATTRIBUTES
        ):
            # Add all attributes under the details.
            details = {}
            for key, value in parsed_response.items():
                if key not in {
                    "label",
                    "reasoning",
                    "version",
                    "totalTokenCount",
                    "inputTokenCount",
                    "outputTokenCount",
                    "finish_reason",
                    "sample_input",
                    "sample_output",
                    "model",
                }:
                    details[key.replace("-", "_")] = value
            result[metric_display_name + "_details"] = details
        result[metric_display_name + "_total_tokens"] = (
            parsed_response["totalTokenCount"] if "totalTokenCount" in parsed_response else ""
        )
        result[metric_display_name + "_prompt_tokens"] = (
            parsed_response["inputTokenCount"] if "inputTokenCount" in parsed_response else ""
        )
        result[metric_display_name + "_completion_tokens"] = (
            parsed_response["outputTokenCount"] if "outputTokenCount" in parsed_response else ""
        )
        result[metric_display_name + "_finish_reason"] = (
            parsed_response["finish_reason"] if "finish_reason" in parsed_response else ""
        )
        result[metric_display_name + "_sample_input"] = (
            parsed_response["sample_input"] if "sample_input" in parsed_response else ""
        )
        result[metric_display_name + "_sample_output"] = (
            parsed_response["sample_output"] if "sample_output" in parsed_response else ""
        )
        result[metric_display_name + "_model"] = parsed_response["model"] if "model" in parsed_response else ""
        return result
    return _parse_content_harm_response(batch_response, metric_name, metric_display_name)


def _parse_content_harm_response(
    batch_response: List[Dict], metric_name: str, metric_display_name: Optional[str] = None
) -> Dict[str, Union[str, float]]:
    """Parse the annotation response from Responsible AI service for a content harm evaluation.

    :param batch_response: The annotation response from Responsible AI service.
    :type batch_response: List[Dict]
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param metric_display_name: The evaluation metric display name to use. If unset, use the metric_name.
    :type metric_display_name: Optional[str]
    :return: The parsed annotation result.
    :rtype: Dict[str, Union[str, float]]
    """
    # Fix the metric name if it's "hate_fairness"
    # Eventually we will remove this fix once the RAI service is updated
    key = metric_name if metric_display_name is None else metric_display_name
    if key == EvaluationMetrics.HATE_FAIRNESS:
        key = EvaluationMetrics.HATE_UNFAIRNESS

    result: Dict[str, Union[str, float]] = {
        (key.value if hasattr(key, "value") else key): math.nan,
        f"{(key.value if hasattr(key, 'value') else key)}_score": math.nan,
        f"{(key.value if hasattr(key, 'value') else key)}_reason": math.nan,
    }

    response = batch_response[0]
    if metric_name not in response:
        return result

    try:
        harm_response = literal_eval(response[metric_name])
    except Exception:  # pylint: disable=broad-exception-caught
        harm_response = response[metric_name]

    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    finish_reason = ""
    sample_input = ""
    sample_output = ""
    model = ""
    if harm_response != "" and isinstance(harm_response, dict):
        # check if "output" is one key in harm_response
        if "output" in harm_response:
            harm_response = harm_response["output"]

        # get content harm metric_value
        if "label" in harm_response:
            try:
                # Handle "n/a" or other non-numeric values
                if isinstance(harm_response["label"], str) and harm_response["label"].strip().lower() == "n/a":
                    metric_value = math.nan
                else:
                    metric_value = float(harm_response["label"])
            except (ValueError, TypeError):
                metric_value = math.nan
        elif "valid" in harm_response:
            metric_value = 0 if harm_response["valid"] else math.nan
        else:
            metric_value = math.nan

        # get reason
        if "reasoning" in harm_response:
            reason = harm_response["reasoning"]
        elif "reason" in harm_response:
            reason = harm_response["reason"]
        else:
            reason = ""

        # get token_usage
        if "totalTokenCount" in harm_response:
            total_tokens = harm_response["totalTokenCount"]
        else:
            total_tokens = 0
        if "inputTokenCount" in harm_response:
            prompt_tokens = harm_response["inputTokenCount"]
        else:
            prompt_tokens = 0
        if "outputTokenCount" in harm_response:
            completion_tokens = harm_response["outputTokenCount"]
        else:
            completion_tokens = 0

        # get finish_reason
        if "finish_reason" in harm_response:
            finish_reason = harm_response["finish_reason"]
        else:
            finish_reason = ""

        # get sample_input
        if "sample_input" in harm_response:
            sample_input = harm_response["sample_input"]
        else:
            sample_input = ""

        # get sample_output
        if "sample_output" in harm_response:
            sample_output = harm_response["sample_output"]
        else:
            sample_output = ""

        # get model
        if "model" in harm_response:
            model = harm_response["model"]
        else:
            model = ""
    elif harm_response != "" and isinstance(harm_response, str):
        metric_value_match = re.findall(r"(\b[0-7])\b", harm_response)
        if metric_value_match:
            metric_value = int(metric_value_match[0])
        else:
            metric_value = math.nan
        reason = harm_response
    elif harm_response != "" and isinstance(harm_response, (int, float)):
        if 0 < harm_response <= 7:
            metric_value = harm_response
        else:
            metric_value = math.nan
        reason = ""
    else:
        metric_value = math.nan
        reason = ""

    harm_score = metric_value
    # We've already handled the "n/a" case by converting to math.nan
    if not math.isnan(metric_value):
        # int(math.nan) causes a value error, and math.nan is already handled
        # by get_harm_severity_level
        harm_score = int(metric_value)
    result[key] = get_harm_severity_level(harm_score)
    result[key + "_score"] = harm_score
    result[key + "_reason"] = reason
    result[key + "_total_tokens"] = total_tokens
    result[key + "_prompt_tokens"] = prompt_tokens
    result[key + "_completion_tokens"] = completion_tokens
    result[key + "_finish_reason"] = finish_reason
    result[key + "_sample_input"] = sample_input
    result[key + "_sample_output"] = sample_output
    result[key + "_model"] = model

    return result


async def _get_service_discovery_url(azure_ai_project: AzureAIProject, token: str) -> str:
    """Get the discovery service URL for the Azure AI project

    :param azure_ai_project: The Azure AI project details.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param token: The Azure authentication token.
    :type token: str
    :return: The discovery service URL.
    :rtype: str
    """
    headers = get_common_headers(token)

    async with get_async_http_client_with_timeout() as client:
        response = await client.get(
            f"https://management.azure.com/subscriptions/{azure_ai_project['subscription_id']}/"
            f"resourceGroups/{azure_ai_project['resource_group_name']}/"
            f"providers/Microsoft.MachineLearningServices/workspaces/{azure_ai_project['project_name']}?"
            f"api-version=2023-08-01-preview",
            headers=headers,
        )

    if response.status_code != 200:
        msg = (
            f"Failed to connect to your Azure AI project. Please check if the project scope is configured correctly, "
            f"and make sure you have the necessary access permissions. "
            f"Status code: {response.status_code}."
        )
        raise EvaluationException(
            message=msg,
            target=ErrorTarget.RAI_CLIENT,
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.PROJECT_ACCESS_ERROR,
            tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
        )

    base_url = urlparse(response.json()["properties"]["discoveryUrl"])
    return f"{base_url.scheme}://{base_url.netloc}"


async def get_rai_svc_url(project_scope: AzureAIProject, token: str) -> str:
    """Get the Responsible AI service URL

    :param project_scope: The Azure AI project scope details.
    :type project_scope: Dict
    :param token: The Azure authentication token.
    :type token: str
    :return: The Responsible AI service URL.
    :rtype: str
    """
    discovery_url = await _get_service_discovery_url(azure_ai_project=project_scope, token=token)
    subscription_id = project_scope["subscription_id"]
    resource_group_name = project_scope["resource_group_name"]
    project_name = project_scope["project_name"]
    base_url = discovery_url.rstrip("/")
    rai_url = (
        f"{base_url}/raisvc/v1.0"
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.MachineLearningServices/workspaces/{project_name}"
    )
    return rai_url


async def fetch_or_reuse_token(
    credential: TokenCredential, token: Optional[str] = None, workspace: Optional[str] = ML_WORKSPACE
) -> str:
    """Get token. Fetch a new token if the current token is near expiry

       :param credential: The Azure authentication credential.
       :type credential:
    ~azure.core.credentials.TokenCredential
       :param token: The Azure authentication token. Defaults to None. If none, a new token will be fetched.
       :type token: str
       :return: The Azure authentication token.
    """
    if token:
        # Decode the token to get its expiration time
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
        except jwt.PyJWTError:
            pass
        else:
            exp_time = decoded_token["exp"]
            current_time = time.time()

            # Return current token if not near expiry
            if (exp_time - current_time) >= 300:
                return token

    return credential.get_token(workspace).token


async def evaluate_with_rai_service(
    data: dict,
    metric_name: str,
    project_scope: Union[str, AzureAIProject],
    credential: TokenCredential,
    annotation_task: str = Tasks.CONTENT_HARM,
    metric_display_name=None,
    evaluator_name=None,
    scan_session_id: Optional[str] = None,
) -> Dict[str, Union[str, float]]:
    """Evaluate the content safety of the response using Responsible AI service (legacy endpoint)

    :param data: The data to evaluate.
    :type data: dict
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param project_scope: The Azure AI project, which can either be a string representing the project endpoint
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
    :type project_scope: Union[str, AzureAIProject]
    :param credential: The Azure authentication credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param annotation_task: The annotation task to use.
    :type annotation_task: str
    :param metric_display_name: The display name of metric to use.
    :type metric_display_name: str
    :param evaluator_name: The evaluator name to use.
    :type evaluator_name: str
    :param scan_session_id: The scan session ID to use for the evaluation.
    :type scan_session_id: Optional[str]
    :return: The parsed annotation result.
    :rtype: Dict[str, Union[str, float]]
    """

    if is_onedp_project(project_scope):
        client = AIProjectClient(
            endpoint=project_scope,
            credential=credential,
            user_agent_policy=UserAgentPolicy(base_user_agent=UserAgentSingleton().value),
        )
        token = await fetch_or_reuse_token(credential=credential, workspace=COG_SRV_WORKSPACE)
        await ensure_service_availability_onedp(client, token, annotation_task)
        operation_id = await submit_request_onedp(
            client, data, metric_name, token, annotation_task, evaluator_name, scan_session_id
        )
        annotation_response = cast(List[Dict], await fetch_result_onedp(client, operation_id, token))
        result = parse_response(annotation_response, metric_name, metric_display_name)
        return result
    else:
        # Get RAI service URL from discovery service and check service availability
        token = await fetch_or_reuse_token(credential)
        rai_svc_url = await get_rai_svc_url(project_scope, token)
        await ensure_service_availability(rai_svc_url, token, annotation_task)

        # Submit annotation request and fetch result
        operation_id = await submit_request(data, metric_name, rai_svc_url, token, annotation_task, evaluator_name)
        annotation_response = cast(List[Dict], await fetch_result(operation_id, rai_svc_url, credential, token))
        result = parse_response(annotation_response, metric_name, metric_display_name)

        return result


def generate_payload_multimodal(content_type: str, messages, metric: str) -> Dict:
    """Generate the payload for the annotation request
    :param content_type: The type of the content representing multimodal or images.
    :type content_type: str
    :param messages: The normalized list of messages to be entered as the "Contents" in the payload.
    :type messages: str
    :param metric: The evaluation metric to use. This determines the task type, and whether a "MetricList" is needed
        in the payload.
    :type metric: str
    :return: The payload for the annotation request.
    :rtype: Dict
    """
    include_metric = True
    task = Tasks.CONTENT_HARM
    if metric == EvaluationMetrics.PROTECTED_MATERIAL:
        task = Tasks.PROTECTED_MATERIAL
        include_metric = False

    if include_metric:
        return {
            "ContentType": content_type,
            "Contents": [{"messages": messages}],
            "AnnotationTask": task,
            "MetricList": [metric],
        }
    return {
        "ContentType": content_type,
        "Contents": [{"messages": messages}],
        "AnnotationTask": task,
    }


async def submit_multimodal_request(messages, metric: str, rai_svc_url: str, token: str) -> str:
    """Submit request to Responsible AI service for evaluation and return operation ID
    :param messages: The normalized list of messages to be entered as the "Contents" in the payload.
    :type messages: str
    :param metric: The evaluation metric to use.
    :type metric: str
    :param rai_svc_url: The Responsible AI service URL.
    :type rai_svc_url: str
    :param token: The Azure authentication token.
    :type token: str
    :return: The operation ID.
    :rtype: str
    """
    ## handle json payload and payload from inference sdk strongly type messages
    if len(messages) > 0 and not isinstance(messages[0], dict):
        try:
            from azure.ai.inference.models import ChatRequestMessage
        except ImportError as ex:
            error_message = (
                "Please install 'azure-ai-inference' package to use SystemMessage, UserMessage, AssistantMessage"
            )
            raise MissingRequiredPackage(message=error_message) from ex
        if len(messages) > 0 and isinstance(messages[0], ChatRequestMessage):
            messages = [message.as_dict() for message in messages]

    filtered_messages = [message for message in messages if message["role"] != "system"]
    assistant_messages = [message for message in messages if message["role"] == "assistant"]
    content_type = retrieve_content_type(assistant_messages, metric)
    payload = generate_payload_multimodal(content_type, filtered_messages, metric)

    ## calling rai service for annotation
    url = rai_svc_url + "/submitannotation"
    headers = get_common_headers(token)
    async with get_async_http_client() as client:
        response = await client.post(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
            url, json=payload, headers=headers
        )
    if response.status_code != 202:
        raise HttpResponseError(
            message=f"Received unexpected HTTP status: {response.status_code} {response.text()}", response=response
        )
    result = response.json()
    operation_id = result["location"].split("/")[-1]
    return operation_id


async def submit_multimodal_request_onedp(client: AIProjectClient, messages, metric: str, token: str) -> str:

    #  handle inference sdk strongly type messages
    if len(messages) > 0 and not isinstance(messages[0], dict):
        try:
            from azure.ai.inference.models import ChatRequestMessage
        except ImportError as ex:
            error_message = (
                "Please install 'azure-ai-inference' package to use SystemMessage, UserMessage, AssistantMessage"
            )
            raise MissingRequiredPackage(message=error_message) from ex
        if len(messages) > 0 and isinstance(messages[0], ChatRequestMessage):
            messages = [message.as_dict() for message in messages]

    ## fetch system and assistant messages from the list of messages
    filtered_messages = [message for message in messages if message["role"] != "system"]
    assistant_messages = [message for message in messages if message["role"] == "assistant"]

    ## prepare for request
    content_type = retrieve_content_type(assistant_messages, metric)
    payload = generate_payload_multimodal(content_type, filtered_messages, metric)
    headers = get_common_headers(token)

    response = client.evaluations.submit_annotation(payload, headers=headers)

    result = json.loads(response)
    operation_id = result["location"].split("/")[-1]
    return operation_id


def _build_sync_eval_payload(
    data: dict, metric_name: str, annotation_task: str, scan_session_id: Optional[str] = None
) -> Dict:
    """Build the sync_evals payload for evaluation using QueryResponseInlineMessage format.

    :param data: The data to evaluate, containing 'query', 'response', and optionally 'context' and 'tool_calls'.
    :type data: dict
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param annotation_task: The annotation task to use.
    :type annotation_task: str
    :param scan_session_id: The scan session ID to use for the evaluation.
    :type scan_session_id: Optional[str]
    :return: The sync_eval payload ready to send to the API.
    :rtype: Dict
    """

    # Build properties/metadata (scenario, category, taxonomy, etc.)
    properties = {}
    if data.get("scenario") is not None:
        properties["scenario"] = data["scenario"]
    if data.get("risk_sub_type") is not None:
        properties["category"] = data["risk_sub_type"]
    if data.get("taxonomy") is not None:
        properties["taxonomy"] = str(data["taxonomy"])  # Ensure taxonomy is converted to string

    # Prepare context if available
    context = None
    if data.get("context") is not None:
        # Handle both string context and dict with contexts list
        context_data = data["context"]
        if isinstance(context_data, str):
            # Context is already a string
            context = context_data
        elif isinstance(context_data, dict) and "contexts" in context_data:
            # Context is a dict with contexts list
            context = " ".join(c["content"] for c in context_data["contexts"])
        elif isinstance(context_data, dict):
            # Context is a dict but might be in a different format
            # Try to get content directly or convert to string
            context = context_data.get("content", str(context_data))

    # Build QueryResponseInlineMessage object
    item_content = QueryResponseInlineMessage(
        query=data.get("query", "query"),  # TODO: remove default query once sync evals supports no query
        response=data.get("response", ""),
        context=context,
        tools=data.get("tool_calls"),
        properties=properties if properties else None,
    )

    # Build the data mapping using mustache syntax {{item.field}}
    data_mapping = {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
    }

    # Create the sync eval input payload
    # Structure: Uses QueryResponseInlineMessage format with azure_ai_evaluator type
    sync_eval_payload = {
        "name": f"Safety Eval - {metric_name}",
        "data_source": {
            "type": "jsonl",
            "source": {"type": "file_content", "content": {"item": item_content}},
        },
        "testing_criteria": [
            {
                "type": "azure_ai_evaluator",
                "name": metric_name,
                "evaluator_name": metric_name,
                "data_mapping": data_mapping,
            }
        ],
    }

    return sync_eval_payload


async def evaluate_with_rai_service_sync(
    data: dict,
    metric_name: str,
    project_scope: Union[str, AzureAIProject],
    credential: TokenCredential,
    annotation_task: str = Tasks.CONTENT_HARM,
    metric_display_name=None,
    evaluator_name=None,
    scan_session_id: Optional[str] = None,
    use_legacy_endpoint: bool = False,
):
    """Evaluate the content safety of the response using Responsible AI service.

    This is the main entry point for RAI service evaluation. By default, uses the sync_evals endpoint.
    Set use_legacy_endpoint=True to use the legacy polling-based annotation endpoint.

    :param data: The data to evaluate.
    :type data: dict
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param project_scope: The Azure AI project, which can either be a string representing the project endpoint
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
    :type project_scope: Union[str, AzureAIProject]
    :param credential: The Azure authentication credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param annotation_task: The annotation task to use.
    :type annotation_task: str
    :param metric_display_name: The display name of metric to use.
    :type metric_display_name: str
    :param evaluator_name: The evaluator name to use.
    :type evaluator_name: str
    :param scan_session_id: The scan session ID to use for the evaluation.
    :type scan_session_id: Optional[str]
    :param use_legacy_endpoint: Whether to use the legacy evaluation endpoint. Defaults to False.
    :type use_legacy_endpoint: bool
    :return: The EvalRunOutputItem containing the evaluation results (or parsed dict if legacy).
    :rtype: Union[EvalRunOutputItem, Dict[str, Union[str, float]]]
    """
    # Route to legacy endpoint if requested
    if use_legacy_endpoint:
        return await evaluate_with_rai_service(
            data=data,
            metric_name=metric_name,
            project_scope=project_scope,
            credential=credential,
            annotation_task=annotation_task,
            metric_display_name=metric_display_name,
            evaluator_name=evaluator_name,
            scan_session_id=scan_session_id,
        )

    # Sync evals endpoint implementation (default)
    api_version = "2025-10-15-preview"
    if not is_onedp_project(project_scope):
        # Get RAI service URL from discovery service and check service availability
        token = await fetch_or_reuse_token(credential)
        rai_svc_url = await get_rai_svc_url(project_scope, token)
        await ensure_service_availability(rai_svc_url, token, annotation_task)

        # Submit annotation request and fetch result
        url = rai_svc_url + f"/sync_evals:run?api-version={api_version}"
        headers = {"aml-user-token": token, "Authorization": "Bearer " + token, "Content-Type": "application/json"}
        sync_eval_payload = _build_sync_eval_payload(data, metric_name, annotation_task, scan_session_id)
        sync_eval_payload_json = json.dumps(sync_eval_payload, cls=SdkJSONEncoder)

        with get_http_client() as client:
            http_response = client.post(url, data=sync_eval_payload_json, headers=headers)

        if http_response.status_code != 200:
            LOGGER.error("Fail evaluating with error message: %s", http_response.text())
            http_response.raise_for_status()
        result = http_response.json()

        return result

    client = AIProjectClient(
        endpoint=project_scope,
        credential=credential,
        user_agent_policy=UserAgentPolicy(base_user_agent=UserAgentSingleton().value),
    )

    sync_eval_payload = _build_sync_eval_payload(data, metric_name, annotation_task, scan_session_id)
    # Call sync_evals.create() with the JSON payload
    eval_result = client.sync_evals.create(eval=sync_eval_payload)

    # Return the raw EvalRunOutputItem for downstream processing
    return eval_result


def _build_sync_eval_multimodal_payload(messages, metric_name: str) -> Dict:
    """Build the sync_evals payload for multimodal evaluations.

    :param messages: The conversation messages to evaluate.
    :type messages: list
    :param metric_name: The evaluation metric name.
    :type metric_name: str
    :return: The payload formatted for sync_evals requests.
    :rtype: Dict
    """

    def _coerce_messages(raw_messages):
        if not raw_messages:
            return []
        if isinstance(raw_messages[0], dict):
            return [copy.deepcopy(message) for message in raw_messages]
        try:
            from azure.ai.inference.models import ChatRequestMessage
        except ImportError as ex:
            error_message = (
                "Please install 'azure-ai-inference' package to use SystemMessage, UserMessage, AssistantMessage"
            )
            raise MissingRequiredPackage(message=error_message) from ex
        if isinstance(raw_messages[0], ChatRequestMessage):
            return [message.as_dict() for message in raw_messages]
        return [copy.deepcopy(message) for message in raw_messages]

    def _normalize_message(message):
        normalized = copy.deepcopy(message)
        content = normalized.get("content")
        if content is None:
            normalized["content"] = []
        elif isinstance(content, list):
            normalized["content"] = [
                copy.deepcopy(part) if isinstance(part, dict) else {"type": "text", "text": str(part)}
                for part in content
            ]
        elif isinstance(content, dict):
            normalized["content"] = [copy.deepcopy(content)]
        else:
            normalized["content"] = [{"type": "text", "text": str(content)}]
        return normalized

    def _content_to_text(parts):
        text_parts = []
        for part in parts:
            if not isinstance(part, dict):
                text_parts.append(str(part))
            elif part.get("text"):
                text_parts.append(part["text"])
            elif part.get("type") in {"image_url", "input_image"}:
                image_part = part.get("image_url") or part.get("image")
                text_parts.append(json.dumps(image_part))
            elif part.get("type") == "input_text" and part.get("text"):
                text_parts.append(part["text"])
            else:
                text_parts.append(json.dumps(part))
        return "\n".join(filter(None, text_parts))

    normalized_messages = [_normalize_message(message) for message in _coerce_messages(messages)]
    filtered_messages = [message for message in normalized_messages if message.get("role") != "system"]

    assistant_messages = [message for message in normalized_messages if message.get("role") == "assistant"]
    user_messages = [message for message in normalized_messages if message.get("role") == "user"]
    content_type = retrieve_content_type(assistant_messages, metric_name)

    last_assistant_text = _content_to_text(assistant_messages[-1]["content"]) if assistant_messages else ""
    last_user_text = _content_to_text(user_messages[-1]["content"]) if user_messages else ""

    if filtered_messages and filtered_messages[-1].get("role") == "assistant":
        response_messages = [filtered_messages[-1]]
        query_messages = filtered_messages[:-1]
    else:
        response_messages = []
        query_messages = filtered_messages

    properties = {}
    if last_user_text:
        properties["query_text"] = last_user_text
    if last_assistant_text:
        properties["response_text"] = last_assistant_text
    if content_type:
        properties["content_type"] = content_type

    item_content = {
        "type": "azure_ai_evaluator_messages",
        "query": query_messages,
        "response": response_messages,
    }
    if properties:
        item_content["properties"] = properties

    template = []
    if "query_text" in properties:
        template.append(
            {
                "type": "message",
                "role": "user",
                "content": {"text": "{{item.properties.query_text}}"},
            }
        )
    if "response_text" in properties:
        template.append(
            {
                "type": "message",
                "role": "assistant",
                "content": {"text": "{{item.properties.response_text}}"},
            }
        )

    data_source = {
        "type": "jsonl",
        "source": {"type": "file_content", "content": {"item": item_content}},
    }
    if template:
        data_source["input_messages"] = {"type": "template", "template": template}

    data_mapping = {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
    }
    if "content_type" in properties:
        data_mapping["content_type"] = "{{item.properties.content_type}}"

    return {
        "name": f"Safety Eval - {metric_name}",
        "data_source": data_source,
        "testing_criteria": [
            {
                "type": "azure_ai_evaluator",
                "name": metric_name,
                "evaluator_name": metric_name,
                "data_mapping": data_mapping,
            }
        ],
    }


async def evaluate_with_rai_service_sync_multimodal(
    messages,
    metric_name: str,
    project_scope: Union[str, AzureAIProject],
    credential: TokenCredential,
    scan_session_id: Optional[str] = None,
    use_legacy_endpoint: bool = False,
):
    """Evaluate multimodal content using Responsible AI service.

    This is the main entry point for multimodal RAI service evaluation. By default, uses the sync_evals endpoint.
    Set use_legacy_endpoint=True to use the legacy polling-based annotation endpoint.

    :param messages: The normalized list of conversation messages.
    :type messages: list
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param project_scope: Azure AI project scope or endpoint.
    :type project_scope: Union[str, AzureAIProject]
    :param credential: Azure authentication credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param scan_session_id: Optional scan session identifier for correlation.
    :type scan_session_id: Optional[str]
    :param use_legacy_endpoint: Whether to use the legacy evaluation endpoint. Defaults to False.
    :type use_legacy_endpoint: bool
    :return: The EvalRunOutputItem or legacy response payload.
    :rtype: Union[Dict, EvalRunOutputItem]
    """
    # Route to legacy endpoint if requested
    if use_legacy_endpoint:
        return await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=metric_name,
            project_scope=project_scope,
            credential=credential,
        )

    # Sync evals endpoint implementation (default)
    api_version = "2025-10-15-preview"
    sync_eval_payload = _build_sync_eval_multimodal_payload(messages, metric_name)

    if is_onedp_project(project_scope):
        client = AIProjectClient(
            endpoint=project_scope,
            credential=credential,
            user_agent_policy=UserAgentPolicy(base_user_agent=UserAgentSingleton().value),
        )

        headers = {"x-ms-client-request-id": scan_session_id} if scan_session_id else None
        if headers:
            return client.sync_evals.create(eval=sync_eval_payload, headers=headers)
        return client.sync_evals.create(eval=sync_eval_payload)

    token = await fetch_or_reuse_token(credential)
    rai_svc_url = await get_rai_svc_url(project_scope, token)
    await ensure_service_availability(rai_svc_url, token, Tasks.CONTENT_HARM)

    url = rai_svc_url + f"/sync_evals:run?api-version={api_version}"
    headers = {
        "aml-user-token": token,
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }
    if scan_session_id:
        headers["x-ms-client-request-id"] = scan_session_id

    sync_eval_payload_json = json.dumps(sync_eval_payload, cls=SdkJSONEncoder)

    with get_http_client() as client:
        http_response = client.post(url, data=sync_eval_payload_json, headers=headers)

    if http_response.status_code != 200:
        LOGGER.error("Fail evaluating with error message: %s", http_response.text())
        http_response.raise_for_status()

    return http_response.json()


async def evaluate_with_rai_service_multimodal(
    messages,
    metric_name: str,
    project_scope: Union[str, AzureAIProject],
    credential: TokenCredential,
):
    """Evaluate the content safety of the response using Responsible AI service (legacy endpoint)
    :param messages: The normalized list of messages.
    :type messages: str
    :param metric_name: The evaluation metric to use.
    :type metric_name: str
    :param project_scope: The Azure AI project, which can either be a string representing the project endpoint
         or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
    :type project_scope: Union[str, AzureAIProject]
    :param credential: The Azure authentication credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :return: The parsed annotation result.
    :rtype: List[List[Dict]]
    """

    if is_onedp_project(project_scope):
        client = AIProjectClient(
            endpoint=project_scope,
            credential=credential,
            user_agent_policy=UserAgentPolicy(base_user_agent=UserAgentSingleton().value),
        )
        token = await fetch_or_reuse_token(credential=credential, workspace=COG_SRV_WORKSPACE)
        await ensure_service_availability_onedp(client, token, Tasks.CONTENT_HARM)
        operation_id = await submit_multimodal_request_onedp(client, messages, metric_name, token)
        annotation_response = cast(List[Dict], await fetch_result_onedp(client, operation_id, token))
        result = parse_response(annotation_response, metric_name)
        return result
    else:
        token = await fetch_or_reuse_token(credential)
        rai_svc_url = await get_rai_svc_url(project_scope, token)
        await ensure_service_availability(rai_svc_url, token, Tasks.CONTENT_HARM)
        # Submit annotation request and fetch result
        operation_id = await submit_multimodal_request(messages, metric_name, rai_svc_url, token)
        annotation_response = cast(List[Dict], await fetch_result(operation_id, rai_svc_url, credential, token))
        result = parse_response(annotation_response, metric_name)
        return result
