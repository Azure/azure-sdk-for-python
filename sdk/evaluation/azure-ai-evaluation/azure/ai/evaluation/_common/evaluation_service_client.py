# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import logging
import time
from typing import Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.evaluation._common.raiclient import AIProjectClient as RestEvaluationServiceClient

from sdk.core.corehttp.corehttp.exceptions import HttpResponseError
from .evaluation_service_interface import EvaluationServiceClientInterface
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from .constants import RAIService

LOGGER = logging.getLogger(__name__)

class EvaluationServiceClient(EvaluationServiceClientInterface):

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self.rest_client = RestEvaluationServiceClient(
            endpoint=endpoint,
            credential=credential,
            **kwargs,
        )

    def check_annotation(self, *, annotation: str, **kwargs) -> None:
        check_annotation_response = self.rest_client.rai_svc.get_annotation(**kwargs)

        if annotation and annotation not in check_annotation_response:
            msg = f"The needed capability '{annotation}' is not supported by the RAI service in this region."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.RAI_CLIENT,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                blame=ErrorBlame.USER_ERROR,
                tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
            )

    async def submit_annotation(self, annotation: dict, **kwargs) -> None:
        submit_annotation_response = self.rest_client.rai_svc.submit_annotation(annotation=annotation, **kwargs)

        annotation_operation_id = submit_annotation_response.location.split("/")[-1]

        def get_operation_result(operation_id: str):
            try:
                return self.rest_client.rai_svc.get_operation_result(operation_id=operation_id)
            except HttpResponseError as e:
                if e.status_code == 201:
                    LOGGER.debug("Annotation operation is still in progress.")
                    return None
                else:
                    raise EvaluationException(
                        message=str(e),
                        internal_message=str(e),
                        target=ErrorTarget.RAI_CLIENT,
                        category=ErrorCategory.SERVICE_UNAVAILABLE,
                        blame=ErrorBlame.USER_ERROR,
                        tsg_link="https://aka.ms/azsdk/python/evaluation/safetyevaluator/troubleshoot",
                    )

        start = time.time()
        request_count = 0
        while True:
            response = get_operation_result(operation_id=annotation_operation_id)
            if response:
                return response
            else:
                request_count += 1
                time_elapsed = time.time() - start
                if time_elapsed > RAIService.TIMEOUT:
                    raise TimeoutError(
                        f"Fetching annotation result {request_count} times out after {time_elapsed:.2f} seconds")

                sleep_time = RAIService.SLEEP_TIME ** request_count
                await asyncio.sleep(sleep_time)


