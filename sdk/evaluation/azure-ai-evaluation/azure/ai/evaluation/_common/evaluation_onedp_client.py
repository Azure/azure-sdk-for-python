# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.evaluation._common.onedp import AIProjectClient as RestEvaluationServiceClient
from azure.ai.evaluation._common.onedp.models import (PendingUploadRequest, PendingUploadType, EvaluationResult,
                                                      ResultType, AssetCredentialRequest, EvaluationUpload, InputDataset)
from azure.storage.blob import ContainerClient
from .utils import upload
from .evaluation_service_interface import EvaluationServiceClientInterface
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

LOGGER = logging.getLogger(__name__)

class EvaluationServiceOneDPClient(EvaluationServiceClientInterface):

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self.rest_client = RestEvaluationServiceClient(
            endpoint=endpoint,
            credential=credential,
            **kwargs,
        )

    def create_evaluation_result(self, *, name: str, path: str, version=1, **kwargs) -> None:
        """Create and upload evaluation results to Azure evaluation service.

        This method uploads evaluation results from a local path to Azure Blob Storage
        and registers them with the evaluation service. The process involves:
        1. Starting a pending upload with the evaluation service
        2. Getting a SAS token for the blob container
        3. Uploading the local evaluation results to the blob container
        4. Creating a version record for the evaluation results

        :param name: The name to identify the evaluation results
        :type name: str
        :param path: The local path to the evaluation results file or directory
        :type path: str
        :param version: The version number for the evaluation results, defaults to 1
        :type version: int, optional
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The response from creating the evaluation result version
        :rtype: EvaluationResult
        :raises: Various exceptions from the underlying API calls or upload process
        """

        LOGGER.debug(f"Creating evaluation result for {name} with version {version} from path {path}")
        start_pending_upload_response = self.rest_client.evaluation_results.start_pending_upload(
            name=name,
            version=version,
            body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
            **kwargs
        )

        LOGGER.debug(f"Uploading {path} to {start_pending_upload_response.blob_reference_for_consumption.blob_uri}")
        with ContainerClient.from_container_url(
            start_pending_upload_response.blob_reference_for_consumption.credential.sas_uri) as container_client:
            upload(path=path, container_client=container_client, logger=LOGGER)

        LOGGER.debug(f"Creating evaluation result version for {name} with version {version}")
        create_version_response = self.rest_client.evaluation_results.create_version(
            body=EvaluationResult(
                blob_uri=start_pending_upload_response.blob_reference_for_consumption.blob_uri,
                result_type=ResultType.EVALUATION,
                name=name,
                version=version
            ),
            name=name,
            version=version,
            **kwargs
        )

        return create_version_response

    def start_evaluation_run(self, *, evaluation: EvaluationUpload, **kwargs) -> EvaluationUpload:
        """Start a new evaluation run in the Azure evaluation service.

        This method creates a new evaluation run with the provided configuration details.

        :param evaluation: The evaluation configuration to upload
        :type evaluation: EvaluationUpload
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The created evaluation run object
        :rtype: EvaluationUpload
        :raises: Various exceptions from the underlying API calls
        """
        upload_run_response = self.rest_client.evaluations.upload_run(
            evaluation=evaluation,
            **kwargs
        )

        return upload_run_response

    def update_evaluation_run(self, *, name: str, evaluation: EvaluationUpload, **kwargs) -> EvaluationUpload:
        """Update an existing evaluation run in the Azure evaluation service.

        This method updates an evaluation run with new information such as status changes,
        result references, or other metadata.

        :param name: The identifier of the evaluation run to update
        :type name: str
        :param evaluation: The updated evaluation configuration
        :type evaluation: EvaluationUpload
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The updated evaluation run object
        :rtype: EvaluationUpload
        :raises: Various exceptions from the underlying API calls
        """
        update_run_response = self.rest_client.evaluations.upload_update_run(
            name=name,
            evaluation=evaluation,
            **kwargs
        )

        return update_run_response

    def check_annotation(self, *, annotation: str, **kwargs) -> None:
        check_annotation_response = self.rest_client.evaluations.check_annotation(**kwargs)

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


