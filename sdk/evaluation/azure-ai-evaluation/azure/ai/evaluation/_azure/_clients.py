# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from logging import Logger
from typing import Any, Dict, Final, Optional, Set, Union, cast
from threading import Lock
from urllib.parse import quote
from json.decoder import JSONDecodeError

from azure.core.credentials import TokenCredential, AzureSasCredential, AccessToken
from azure.core.rest import HttpResponse
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import HttpPipeline, get_http_client
from azure.ai.evaluation._azure._token_manager import AzureMLTokenManager
from azure.ai.evaluation._constants import TokenScope
from ._models import BlobStoreInfo, Workspace


API_VERSION: Final[str] = "2024-07-01-preview"
QUERY_KEY_API_VERSION: Final[str] = "api-version"
PATH_ML_WORKSPACES = ("providers", "Microsoft.MachineLearningServices", "workspaces")


class LiteMLClient:
    """A lightweight Azure ML API client.

    :param subscription_id: Azure subscription ID
    :type subscription_id: str
    :param resource_group: Azure resource group name
    :type resource_group: str
    :param logger: Logger object
    :type logger: logging.Logger
    :keyword credential: Azure credentials
    :paramtype credential: TokenCredential
    :keyword kwargs: Additional keyword arguments
    :paramtype kwargs: Dict
    :keyword str api_version: The API version. Default is 2024-10-01
    """

    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        logger: Logger,
        credential: Optional[TokenCredential] = None,
        **kwargs: Any,
    ) -> None:
        subscription_id = quote(subscription_id, safe="")
        resource_group = quote(resource_group, safe="")

        self._base_url: Final[str] = (
            f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        )
        self._logger: Final[Logger] = logger
        self._api_version: Final[str] = kwargs.get("api_version", API_VERSION)
        self._http_client: Final[HttpPipeline] = get_http_client(**kwargs)
        self._lock: Final[Lock] = Lock()

        # things that can change under lock
        self._token_manager: Optional[AzureMLTokenManager] = None
        self._credential: Optional[TokenCredential] = credential

    def get_token(self) -> AccessToken:
        return self._get_token_manager().get_token()

    def get_credential(self) -> TokenCredential:
        # load the token manager to get the credential if needed
        self._get_token_manager()
        return cast(TokenCredential, self._credential)

    def workspace_get_default_datastore(
        self, workspace_name: str, *, include_credentials: bool = False, **kwargs: Any
    ) -> BlobStoreInfo:
        # 1. Get the default blob store
        # REST API documentation:
        # https://learn.microsoft.com/rest/api/azureml/datastores/list?view=rest-azureml-2024-10-01
        url = self._generate_path(  # pylint: disable=specify-parameter-names-in-call
            *PATH_ML_WORKSPACES, workspace_name, "datastores"
        )
        headers = self._get_headers()

        stores_response = self._http_client.request(
            method="GET",
            url=url,
            params={QUERY_KEY_API_VERSION: self._api_version, "isDefault": True, "count": 1, "orderByAsc": "false"},
            headers=headers,
        )
        self._throw_on_http_error(stores_response, "list default workspace datastore")

        json = stores_response.json()["value"][0]
        props_json = json["properties"]
        name = json["name"]
        account_name = props_json["accountName"]
        endpoint = props_json["endpoint"]
        container_name = props_json["containerName"]
        credential_type = props_json.get("credentials", {}).get("credentialsType")

        # 2. Get the SAS token to use for accessing the blob store
        # REST API documentation:
        # https://learn.microsoft.com/rest/api/azureml/datastores/list-secrets?view=rest-azureml-2024-10-01
        blob_store_credential: Optional[Union[AzureSasCredential, TokenCredential, str]]
        if not include_credentials:
            blob_store_credential = None
        elif credential_type and credential_type.lower() == "none":
            # If storage account key access is disabled, and only Microsoft Entra ID authentication is available,
            # the credentialsType will be "None" and we should not attempt to get the secrets.
            blob_store_credential = self.get_credential()
        else:
            url = self._generate_path(
                *PATH_ML_WORKSPACES, workspace_name, "datastores", "workspaceblobstore", "listSecrets"
            )
            secrets_response = self._http_client.request(
                method="POST",
                url=url,
                json={
                    "expirableSecret": True,
                    "expireAfterHours": int(kwargs.get("key_expiration_hours", 1)),
                },
                params={
                    QUERY_KEY_API_VERSION: self._api_version,
                },
                headers=headers,
            )
            self._throw_on_http_error(secrets_response, "workspace datastore secrets")

            secrets_json = secrets_response.json()
            secrets_type = secrets_json["secretsType"].lower()

            # As per this website, only SAS tokens, access tokens, or Entra IDs are valid for accessing blob data
            # stores:
            # https://learn.microsoft.com/rest/api/storageservices/authorize-requests-to-azure-storage.
            if secrets_type == "sas":
                blob_store_credential = AzureSasCredential(secrets_json["sasToken"])
            elif secrets_type == "accountkey":
                # To support older versions of azure-storage-blob better, we return a string here instead of
                # an AzureNamedKeyCredential
                blob_store_credential = secrets_json["key"]
            else:
                raise EvaluationException(
                    message=f"The '{account_name}' blob store does not use a recognized credential type.",
                    internal_message=f"The credential type is '{secrets_type}'",
                    target=ErrorTarget.EVALUATE,
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )

        return BlobStoreInfo(name, account_name, endpoint, container_name, blob_store_credential)

    def workspace_get_info(self, workspace_name: str) -> Workspace:
        # https://learn.microsoft.com/rest/api/azureml/workspaces/get?view=rest-azureml-2024-10-01
        workspace_response = self._http_client.request(
            "GET",
            self._generate_path(*PATH_ML_WORKSPACES, workspace_name),
            params={QUERY_KEY_API_VERSION: self._api_version},
            headers=self._get_headers(),
        )

        self._throw_on_http_error(workspace_response, f"get '{workspace_name}' workspace")
        workspace = Workspace.deserialize(workspace_response)
        return workspace

    def _get_token_manager(self) -> AzureMLTokenManager:
        # Lazy init since getting credentials in the constructor can take a long time in some situations
        if self._token_manager is None:
            with self._lock:
                if self._token_manager is None:
                    self._token_manager = AzureMLTokenManager(
                        TokenScope.DEFAULT_AZURE_MANAGEMENT.value, self._logger, credential=self._credential
                    )
                    self._credential = self._token_manager.credential

        return self._token_manager

    @staticmethod
    def _throw_on_http_error(response: HttpResponse, description: str, valid_status: Optional[Set[int]] = None) -> None:
        if valid_status and (response.status_code in valid_status):
            return
        if response.status_code >= 200 and response.status_code < 300:
            # nothing to see here, move along
            return

        message = f"The {description} request failed with HTTP {response.status_code}"
        try:
            error_json = response.json()["error"]
            additional_info = f"({error_json['code']}) {error_json['message']}"
            message += f" - {additional_info}"
        except (JSONDecodeError, ValueError, KeyError):
            pass

        raise EvaluationException(
            message=message,
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.FAILED_EXECUTION,
            blame=ErrorBlame.SYSTEM_ERROR,
        )

    def _generate_path(self, *paths: str) -> str:
        sanitized_paths = [quote(path, safe="") for path in paths]
        url = self._base_url + "/" + str.join("/", sanitized_paths)
        return url

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.get_token().token}", "Content-Type": "application/json"}
