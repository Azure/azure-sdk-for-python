# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Union, Any, Dict
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.evaluation._common.onedp import AIProjectClient as RestEvaluationServiceClient
from azure.ai.evaluation._common.onedp.models import (PendingUploadRequest, PendingUploadType, EvaluationResult,
                                                      ResultType, AssetCredentialRequest, EvaluationUpload, InputDataset, RedTeamUpload)
from azure.storage.blob import ContainerClient
from .utils import upload

LOGGER = logging.getLogger(__name__)

class EvaluationServiceOneDPClient:

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self.rest_client = RestEvaluationServiceClient(
            endpoint=endpoint,
            credential=credential,
            **kwargs,
        )

    def create_evaluation_result(
            self, *, name: str, path: str, version=1, metrics: Dict[str, int]=None, result_type: ResultType=ResultType.EVALUATION, **kwargs) -> EvaluationResult:
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
        :param metrics: Metrics to be added to evaluation result
        :type metrics: Dict[str, int], optional
        :param result_type: Evaluation Result Type to create
        :type result_type: ResultType, optional
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The response from creating the evaluation result version
        :rtype: EvaluationResult
        :raises: Various exceptions from the underlying API calls or upload process
        """

        LOGGER.debug(f"Creating evaluation result for {name} with version {version} type {result_type} from path {path}")
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
        create_version_response = self.rest_client.evaluation_results.create_or_update_version(
            body=EvaluationResult(
                blob_uri=start_pending_upload_response.blob_reference_for_consumption.blob_uri,
                result_type=result_type,
                name=name,
                version=version,
                metrics=metrics,
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

    def start_red_team_run(self, *, red_team: RedTeamUpload, **kwargs):
        """Start a new red team run in the Azure evaluation service.

        This method creates a new red team run with the provided configuration details.

        :param red_team: The red team configuration to upload
        :type red_team: ~azure.ai.evaluation._common.onedp.models.RedTeamUpload
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The created red team run object
        :rtype: ~azure.ai.evaluation._common.onedp.models.RedTeamUpload
        :raises: Various exceptions from the underlying API calls
        """
        upload_run_response = self.rest_client.red_teams.upload_run(
            redteam=red_team,
            **kwargs
        )

        return upload_run_response

    def update_red_team_run(self, *, name: str, red_team: RedTeamUpload, **kwargs):
        """Update an existing red team run in the Azure evaluation service.

        This method updates a red team run with new information such as status changes,
        result references, or other metadata.

        :param name: The identifier of the red team run to update
        :type name: str
        :param red_team: The updated red team configuration
        :type red_team: ~azure.ai.evaluation._common.onedp.models.RedTeamUpload
        :param kwargs: Additional keyword arguments to pass to the underlying API calls
        :return: The updated red team run object
        :rtype: ~azure.ai.evaluation._common.onedp.models.RedTeamUpload
        :raises: Various exceptions from the underlying API calls
        """
        update_run_response = self.rest_client.red_teams.upload_update_run(
            name=name,
            redteam=red_team,
            **kwargs
        )

        return update_run_response