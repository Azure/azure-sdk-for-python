# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# flake8: noqa
# type: ignore
import os
from typing import Any, Dict
from urllib.parse import urljoin, urlparse
import json
import asyncio
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import AsyncHttpPipeline, get_async_http_client, get_http_client
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._user_agent import USER_AGENT
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryMode

from ._identity_manager import APITokenManager

api_url = None
if "RAI_SVC_URL" in os.environ:
    api_url = os.environ["RAI_SVC_URL"]
    api_url = api_url.rstrip("/")
    print(f"Found RAI_SVC_URL in environment variable, using {api_url} for the service endpoint.")

# TODO: remove this
api_url = "https://int.api.azureml-test.ms"


class RAIClient:  # pylint: disable=client-accepts-api-version-keyword
    """Client for the Responsible AI Service

    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param token_manager: The token manager
    :type token_manage: ~azure.ai.evaluation.simulator._model_tools._identity_manager.APITokenManager
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
        self, azure_ai_project: AzureAIProject, token_manager: APITokenManager
    ) -> None:
        self.azure_ai_project = azure_ai_project
        self.token_manager = token_manager

        self.contentharm_parameters = None
        self.jailbreaks_dataset = None

        if api_url is not None:
            host = api_url

        else:
            host = self._get_service_discovery_url()
        segments = [
            host.rstrip("/"),
            "raisvc/v1.0/subscriptions",
            self.azure_ai_project["subscription_id"],
            "resourceGroups",
            self.azure_ai_project["resource_group_name"],
            "providers/Microsoft.MachineLearningServices/workspaces",
            self.azure_ai_project["project_name"],
        ]
        self.api_url = "/".join(segments)
        # add a "/" at the end of the url
        self.api_url = self.api_url.rstrip("/") + "/"
        self.parameter_json_endpoint = urljoin(self.api_url, "simulation/template/parameters")
        self.jailbreaks_json_endpoint = urljoin(self.api_url, "simulation/jailbreak")
        self.simulation_submit_endpoint = urljoin(self.api_url, "simulation/chat/completions/submit")
        self.xpia_jailbreaks_json_endpoint = urljoin(self.api_url, "simulation/jailbreak/xpia")

    def _get_service_discovery_url(self):
        bearer_token = self.token_manager.get_token()
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        http_client = get_http_client()
        response = http_client.get(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
            f"https://management.azure.com/subscriptions/{self.azure_ai_project['subscription_id']}/"
            f"resourceGroups/{self.azure_ai_project['resource_group_name']}/"
            f"providers/Microsoft.MachineLearningServices/workspaces/{self.azure_ai_project['project_name']}?"
            f"api-version=2023-08-01-preview",
            headers=headers,
            timeout=5,
        )
        if response.status_code != 200:
            msg = "Failed to retrieve the discovery service URL."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.RAI_CLIENT,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                blame=ErrorBlame.UNKNOWN,
            )
        base_url = urlparse(response.json()["properties"]["discoveryUrl"])
        return f"{base_url.scheme}://{base_url.netloc}"

    def _create_async_client(self) -> AsyncHttpPipeline:
        """Create an async http client with retry mechanism

        Number of retries is set to 6, and the timeout is set to 5 seconds.

        :return: The async http client
        :rtype: ~azure.ai.evaluation._http_utils.AsyncHttpPipeline
        """
        return get_async_http_client().with_policies(
            retry_policy=AsyncRetryPolicy(retry_total=6, retry_backoff_factor=5, retry_mode=RetryMode.Fixed)
        )

    async def get_contentharm_parameters(self) -> Any:
        """Get the content harm parameters, if they exist"""
        if self.contentharm_parameters is None:
            self.contentharm_parameters = await self.get(self.parameter_json_endpoint)

        return self.contentharm_parameters

    async def get_jailbreaks_dataset(self, type: str) -> Any:
        """Get the jailbreaks dataset, if exists

        :param type: The dataset type. Should be one of 'xpia' or 'upia'
        :type type: str
        """
        if self.jailbreaks_dataset is None:
            if type == "xpia":
                self.jailbreaks_dataset = await self.get(self.xpia_jailbreaks_json_endpoint)
            elif type == "upia":
                self.jailbreaks_dataset = await self.get(self.jailbreaks_json_endpoint)
            else:
                msg = f"Invalid jailbreak type: {type}. Supported types: ['xpia', 'upia']"
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    target=ErrorTarget.ADVERSARIAL_SIMULATOR,
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.USER_ERROR,
                )

        return self.jailbreaks_dataset

    async def get(self, url: str) -> Any:
        """Make a GET request to the given url

        :param url: The url
        :type url: str
        :raises EvaluationException: If the Azure safety evaluation service is not available in the current region
        :return: The response
        :rtype: Any
        """
        token = self.token_manager.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }

        session = self._create_async_client()

        async with session:
            response = await session.get(url=url, headers=headers)  # pylint: disable=unexpected-keyword-arg

        if response.status_code == 200:
            return response.json()

        msg = (
            "Azure safety evaluation service is not available in your current region, "
            + "please go to https://aka.ms/azureaistudiosafetyeval to see which regions are supported"
        )
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.RAI_CLIENT,
            category=ErrorCategory.UNKNOWN,
            blame=ErrorBlame.USER_ERROR,
        )

    async def customize_first_turn(
        self,
        *,
        template_key: str,
        personality: str,
        application_scenario: str,
        other_template_kwargs: Any = {},
        logger: Any = None,
    ) -> Any:
        token = self.token_manager.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        # TODO: change URL
        json_payload = {
            "url": self.simulation_submit_endpoint,
            "headers": {
                "Content-Type": "application/json",
            },
            "json": '{"messages": [{"role": "system", "content": "{{ch_template_placeholder}}"}], "temperature": 0.0, "max_tokens": 4096, "n": 1, "frequency_penalty": 0, "presence_penalty": 0, "stop": ["<|im_end|>", "<|endoftext|>"]}',
            "params": {"api-version": "2023-07-01-preview"},
            "templatekey": str(template_key),
            "templateParameters": {
                "personality": str(personality),
                "application_scenario": str(application_scenario),
                **other_template_kwargs,
            },
            "simulationType": "CustomPersona",
        }
        session = self._create_async_client()
        async with session:
            response = await session.post(
                url=self.simulation_submit_endpoint, headers=headers, json=json_payload
            )  # pylint: disable=unexpected-keyword-arg

        if response.status_code != 202:
            raise HttpResponseError(
                message=f"Received unexpected HTTP status: {response.status_code} {response.text()}", response=response
            )

        response = response.json()
        result_url = response["location"]

        retry_policy = AsyncRetryPolicy(  # set up retry configuration
            retry_on_status_codes=[202],  # on which statuses to retry
            retry_total=7,
            retry_backoff_factor=10.0,
            retry_backoff_max=180,
            retry_mode=RetryMode.Exponential,
        )

        # # initial 15 seconds wait before attempting to fetch result
        await asyncio.sleep(15)
        import time

        time.sleep(15)

        async with get_async_http_client().with_policies(retry_policy=retry_policy) as exp_retry_client:
            response = await exp_retry_client.get(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
                result_url, headers=headers
            )
            logger.info(f"Retrying.... {result_url}")
        response.raise_for_status()
        try:
            logger.info(f"Parsing response from {result_url}")
            response_data = response.json()
            response_content = response_data["choices"][0]["message"]["content"]
            logger.info(f"Response from {result_url} is {response_content}")
            logger.info(f"full response: {json.dumps(response_data)}")
            return response_content, response_data
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            import pdb

            pdb.set_trace()
            return None
