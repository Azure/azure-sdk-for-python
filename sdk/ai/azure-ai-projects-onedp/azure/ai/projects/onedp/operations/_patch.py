# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
import inspect
from typing import List, Optional, Any, Tuple, Iterable
from pathlib import Path
from urllib.parse import urlparse
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace
from ._operations import DatasetsOperations as DatasetsOperationsGenerated
from ..models._models import DatasetVersion, PendingUploadRequest, PendingUploadType, PendingUploadResponse, Connection
from ..models._enums import (
    DatasetType,
    AuthenticationType,
    ConnectionType,
)

logger = logging.getLogger(__name__)

class AssistantsOperations:

    # TODO: Merge all code related to handling user-agent, into a single place.
    def __init__(self, outer_instance: "AIProjectClient") -> None:

        # All returned inference clients will have this application id set on their user-agent.
        # For more info on user-agent HTTP header, see:
        # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
        USER_AGENT_APP_ID = "AIProjectClient"

        if hasattr(outer_instance, "_user_agent") and outer_instance._user_agent:
            # If the calling application has set "user_agent" when constructing the AIProjectClient,
            # take that value and prepend it to USER_AGENT_APP_ID.
            self._user_agent = f"{outer_instance._user_agent}-{USER_AGENT_APP_ID}"
        else:
            self._user_agent = USER_AGENT_APP_ID

        self._outer_instance = outer_instance

    @distributed_trace
    def get_client(self, **kwargs) -> "AssistantClient":
        """Get an authenticated AssistantClient (from the package azure-ai-assistants) to use with
        your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        .. note:: The package `azure-ai-assistants` must be installed prior to calling this method.

        :return: An authenticated Assistant Client.
        :rtype: ~azure.ai.assistants.AssistantClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-assistants` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.assistants import AssistantClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Assistant SDK is not installed. Please install it using 'pip install azure-ai-assistants'"
            ) from e

        client = AssistantClient(
            endpoint=self._outer_instance._config.endpoint,
            credential=self._outer_instance._config.cedential,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client


class InferenceOperations:

    def __init__(self, outer_instance: "AIProjectClient") -> None:

        # All returned inference clients will have this application id set on their user-agent.
        # For more info on user-agent HTTP header, see:
        # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
        USER_AGENT_APP_ID = "AIProjectClient"

        if hasattr(outer_instance, "_user_agent") and outer_instance._user_agent:
            # If the calling application has set "user_agent" when constructing the AIProjectClient,
            # take that value and prepend it to USER_AGENT_APP_ID.
            self._user_agent = f"{outer_instance._user_agent}-{USER_AGENT_APP_ID}"
        else:
            self._user_agent = USER_AGENT_APP_ID

        self._outer_instance = outer_instance

    @classmethod
    def _get_inference_url(cls, input_url: str) -> str:
        """
        Converts an input URL in the format:
        https://<host-name>/<some-path>
        to:
        https://<host-name>/api/models
        """
        parsed = urlparse(input_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Invalid endpoint URL format. Must be an https URL with a host.")
        new_url = f"https://{parsed.netloc}/api/models"
        return new_url

    @distributed_trace
    def get_chat_completions_client(self, **kwargs) -> "ChatCompletionsClient":
        """Get an authenticated ChatCompletionsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports chat completions must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated chat completions client.
        :rtype: ~azure.ai.inference.ChatCompletionsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_embeddings_client(self, **kwargs) -> "EmbeddingsClient":
        """Get an authenticated EmbeddingsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports text embeddings must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated Embeddings client.
        :rtype: ~azure.ai.inference.EmbeddingsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import EmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = EmbeddingsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_image_embeddings_client(self, **kwargs) -> "ImageEmbeddingsClient":
        """Get an authenticated ImageEmbeddingsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports image embeddings must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated Image Embeddings client.
        :rtype: ~azure.ai.inference.ImageEmbeddingsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import ImageEmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = ImageEmbeddingsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_azure_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "AzureOpenAI":
        """Get an authenticated AzureOpenAI client (from the `openai` package) for the default
        Azure OpenAI connection (if `connection_name` is not specificed), or from the Azure OpenAI
        resource given by its connection name.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: str
        :keyword connection_name: The name of a connection to an Azure OpenAI resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure OpenAI connection will be used.
        :type connection_name: str

        :return: An authenticated AzureOpenAI client
        :rtype: ~openai.AzureOpenAI

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure OpenAI connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `openai` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        try:
            from openai import AzureOpenAI
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenAI SDK is not installed. Please install it using 'pip install openai'"
            ) from e

        if connection_name:
            connection = self._outer_instance.connections.get(name=connection_name, **kwargs)
        else:
            # If connection name was not specified, get the default Azure OpenAI connection.
            connections = self._outer_instance.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI,
                default_connection=True,
                **kwargs
            )
            connection = next(iter(connections), None)
            if not connection:
                raise ResourceNotFoundError("No default Azure OpenAI connection found.")
            connection_name = connection.name

        # If the connection uses API key authentication, we need to make another service call to get 
        # the connection with API key populated.
        if connection.auth_type == AuthenticationType.API_KEY:
            connection = self._outer_instance.connections.get_with_credentials(name=connection_name, **kwargs)

        logger.debug("[InferenceOperations.get_azure_openai_client] connection = %s", str(connection))

        azure_endpoint = connection.target[:-1] if connection.target.endswith("/") else connection.target

        if connection.auth_type == AuthenticationType.API_KEY:

            api_key = connection.credentials.key

            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)

        elif connection.auth_type == AuthenticationType.ENTRA_ID:

            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication"
            )

            try:
                from azure.identity import get_bearer_token_provider
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                ) from e

            client = AzureOpenAI(
                # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
                azure_ad_token_provider=get_bearer_token_provider(
                    self._outer_instance._config.credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=azure_endpoint,
                api_version=api_version,
            )

        else:
            raise ValueError("Unsupported authentication type {connection.auth_type}")

        return client


class TelemetryOperations:

    _connection_string: Optional[str] = None

    def __init__(self, outer_instance: "AIProjectClient") -> None:
        self._outer_instance = outer_instance

    @distributed_trace
    def get_connection_string(self) -> str:
        """Get the Application Insights connection string associated with the Project's Application Insights resource.

        :return: The Application Insights connection string if a the resource was enabled for the Project.
        :rtype: str
        :raises ~azure.core.exceptions.ResourceNotFoundError: An Application Insights resource was not
            enabled for this project.
        """
        if not self._connection_string:

            # TODO: Test what happens here when there is no AppInsights connection. Does this throw or just returns an empty list?
            connections: Iterable[Connection] = self._outer_instance.connections.list(
                connection_type=ConnectionType.APPLICATION_INSIGHTS
            )

            # Read AppInsights connection string from the first connection in the list.
            for connection in connections:
                self._connection_string = connection.metadata.get("connection_string")
                break

            if not self._connection_string:
                raise ResourceNotFoundError("Application Insights resource was not enabled for this Project.")

        return self._connection_string


class DatasetsOperations(DatasetsOperationsGenerated):

    # Internal helper method to create a new dataset and return a ContainerClient from azure-storage-blob package,
    # to the dataset's blob storage.
    def _create_dataset_and_get_its_container_client(
        self,
        name: str,
        input_version: Optional[str] = None,
    ) -> Tuple[ContainerClient, str]:

        if input_version:
            pending_upload_response: PendingUploadResponse = self.start_pending_upload_version(
                name=name,
                version=input_version,
                body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
            )
            output_version: str = input_version
        else:
            pending_upload_response: PendingUploadResponse = self.start_pending_upload(
                name=name,
                body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
            )
            if pending_upload_response.dataset_version:
                output_version: str = pending_upload_response.dataset_version
            else:
                raise ValueError("Dataset version is not present in the response")

        if not pending_upload_response.blob_reference_for_consumption:
            raise ValueError("Blob reference for consumption is not present")
        if not pending_upload_response.blob_reference_for_consumption.credential.type:
            raise ValueError("Credential type is not present")
        if pending_upload_response.blob_reference_for_consumption.credential.type != AuthenticationType.SAS:
            raise ValueError("Credential type is not SAS")
        if not pending_upload_response.blob_reference_for_consumption.blob_uri:
            raise ValueError("Blob URI is not present or empty")

        if logger.getEffectiveLevel() == logging.DEBUG:
            method = inspect.currentframe().f_code.co_name if inspect.currentframe() else "unknown"
            logger.debug(
                "[%s] pending_upload_response.pending_upload_id = %s.",
                method,
                pending_upload_response.pending_upload_id,
            )
            logger.debug(
                "[%s] pending_upload_response.pending_upload_type = %s.",
                method,
                pending_upload_response.pending_upload_type,
            )  # == PendingUploadType.TEMPORARY_BLOB_REFERENCE
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.blob_uri = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.blob_uri,
            )  # Hosted on behalf of (HOBO) not visible to the user. If the form of: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.storage_account_arm_id = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.storage_account_arm_id,
            )  # /subscriptions/<>/resourceGroups/<>/Microsoft.Storage/accounts/<>
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.credential.sas_uri = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.credential.sas_uri,
            )
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.credential.type = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.credential.type,
            )  # == AuthenticationType.SAS

        # For overview on Blob storage SDK in Python see:
        # https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
        # https://learn.microsoft.com/azure/storage/blobs/storage-blob-upload-python

        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-from-container-url
        return (
            ContainerClient.from_container_url(
                container_url=pending_upload_response.blob_reference_for_consumption.blob_uri,  # Of the form: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            ),
            output_version,
        )

    def upload_file_and_create(
        self, *, name: str, version: str, file: str, **kwargs: Any
    ) -> DatasetVersion:
        """Upload file to a blob storage, and create a dataset that references this file.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload the file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :param name: The name of the dataset. Required.
        :type name: str
        :param version: The version identifier for the dataset. Required.
        :type version: str
        :param file: The file name (including optional path) to be uploaded. Required.
        :type file: str
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.DatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """

        path_file = Path(file)
        if not path_file.exists():
            raise ValueError("The provided file does not exist.")
        if path_file.is_dir():
            raise ValueError("The provided file is actually a folder. Use method `create_and_upload_folder` instead")

        container_client, output_version = self._create_dataset_and_get_its_container_client(
            name=name, input_version=version
        )

        with container_client:

            with open(file=file, mode="rb") as data:

                blob_name = path_file.name  # Extract the file name from the path.
                logger.debug(
                    "[%s] Start uploading file `%s` as blob `%s`.",
                    inspect.currentframe().f_code.co_name,
                    file,
                    blob_name,
                )

                # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                with container_client.upload_blob(name=blob_name, data=data, **kwargs) as blob_client:

                    logger.debug("[%s] Done uploading", inspect.currentframe().f_code.co_name)

                    dataset_version = self.create_version(
                        name=name,
                        version=output_version,
                        body=DatasetVersion(
                            # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                            # Per above doc the ".url" contains SAS token... should this be stripped away?
                            dataset_uri=blob_client.url,  # "<account>.blob.windows.core.net/<container>/<file_name>"
                            type=DatasetType.URI_FILE,
                        ),
                    )

        return dataset_version

    def upload_folder_and_create(
        self, *, name: str, version: str, folder: str, **kwargs: Any
    ) -> DatasetVersion:
        """Upload all files in a folder and its sub folders to a blob storage, while maintaining
        relative paths, and create a dataset that references this folder.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload each file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :param name: The name of the dataset. Required.
        :type name: str
        :param version: The version identifier for the dataset. Required.
        :type version: str
        :param folder: The folder name (including optional path) to be uploaded. Required.
        :type file: str
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.DatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """
        path_folder = Path(folder)
        if not Path(path_folder).exists():
            raise ValueError("The provided folder does not exist.")
        if Path(path_folder).is_file():
            raise ValueError("The provided folder is actually a file. Use method `create_and_upload_file` instead.")

        container_client, output_version = self._create_dataset_and_get_its_container_client(
            name=name, input_version=version
        )

        with container_client:

            # Recursively traverse all files in the folder
            files_uploaded: bool = False
            for file_path in path_folder.rglob("*"):  # `rglob` matches all files and folders recursively
                if file_path.is_file():  # Check if the path is a file. Skip folders.
                    blob_name = file_path.relative_to(path_folder)  # Blob name relative to the folder
                    logger.debug(
                        "[%s] Start uploading file `%s` as blob `%s`.",
                        inspect.currentframe().f_code.co_name,
                        file_path,
                        blob_name,
                    )
                    with file_path.open("rb") as data:  # Open the file for reading in binary mode
                        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                        container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    logger.debug("[%s] Done uploaded.", inspect.currentframe().f_code.co_name)
                    files_uploaded = True

            if not files_uploaded:
                raise ValueError("The provided folder is empty.")

            dataset_version = self.create_version(
                name=name,
                version=output_version,
                body=DatasetVersion(
                    # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                    # Per above doc the ".url" contains SAS token... should this be stripped away?
                    dataset_uri=container_client.url,  # "<account>.blob.windows.core.net/<container> ?"
                    type=DatasetType.URI_FOLDER,
                ),
            )

        return dataset_version


__all__: List[str] = [
    "InferenceOperations",
    "TelemetryOperations",
    "DatasetsOperations",
    "AssistantsOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
