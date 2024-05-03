# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List, Union, overload, Optional, cast, Tuple, TypeVar, Dict
from enum import Enum
import json
import datetime

from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.pipeline import PipelineResponse
from azure.core.rest import (
    HttpResponse,
    AsyncHttpResponse,
    HttpRequest,
)
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)

from .models import (
    TranslationStatus,
    DocumentStatus,
    DocumentTranslationInput,
    DocumentTranslationFileFormat,
    StorageInputType,
    TranslationGlossary,
    TranslationTarget,
    DocumentTranslationError,
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    TargetInput as _TargetInput,
    DocumentFilter as _DocumentFilter,
    StartTranslationDetails as _StartTranslationDetails,
)
from .models._models import (
    TranslationStatus as _TranslationStatus,
    DocumentStatus as _DocumentStatus,
)
from .models._patch import convert_status

COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"
POLLING_INTERVAL = 1

ResponseType = Union[HttpResponse, AsyncHttpResponse]
PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


class DocumentTranslationLROPoller(LROPoller[PollingReturnType_co]):
    """A custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :return: The str ID for the translation operation.
        :rtype: str
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return self._polling_method._current_body.id  # pylint: disable=protected-access
        return self._polling_method._get_id_from_headers()  # pylint: disable=protected-access

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :return: The details for the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return TranslationStatus._from_generated(  # pylint: disable=protected-access
                self._polling_method._current_body  # pylint: disable=protected-access
            )
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # pylint: disable=protected-access

    @classmethod
    def from_continuation_token(  # pylint: disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype
        cls, polling_method, continuation_token, **kwargs: Any
    ):
        """
        :meta private:
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class DocumentTranslationLROPollingMethod(LROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> _TranslationStatus:
        try:
            return _TranslationStatus(self._pipeline_response.http_response.json())
        except json.decoder.JSONDecodeError:
            return _TranslationStatus()

    def _get_id_from_headers(self) -> str:
        return (
            self._initial_response.http_response.headers["Operation-Location"]
            .split("/batches/")[1]
            .split("?api-version")[0]
        )

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, self._cont_token_response, deserialization_callback

    def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            self.update_status()
        while not self.finished():
            self._delay()
            self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class TranslationPolling(OperationResourcePolling):
    """Implements a Location polling."""

    def can_poll(self, pipeline_response: PipelineResponseType) -> bool:
        """Answer if this polling method could be used.

        :param pipeline_response: The PipelineResponse type
        :type pipeline_response: PipelineResponseType
        :return: Whether polling should be performed.
        :rtype: bool
        """
        response = pipeline_response.http_response
        can_poll = self._operation_location_header in response.headers
        if can_poll:
            return True

        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return True
        return False

    def _set_async_url_if_present(self, response: ResponseType) -> None:
        location_header = response.headers.get(self._operation_location_header)
        if location_header:
            self._async_url = location_header
        else:
            self._async_url = response.request.url

    def get_status(self, pipeline_response: PipelineResponseType) -> str:
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse pipeline_response: latest REST call response.
        :return: The current operation status
        :rtype: str
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return self._map_nonstandard_statuses(status, body)
            raise BadResponse("No status found in body")
        raise BadResponse("The response from long running operation does not contain a body.")

    def _map_nonstandard_statuses(self, status: str, body: Dict[str, Any]) -> str:
        """Map non-standard statuses.

        :param str status: lro process status.
        :param str body: pipeline response body.
        :return: The current operation status.
        :rtype: str
        """
        if status == "ValidationFailed":
            self.raise_error(body)
        return status

    def raise_error(self, body: Dict[str, Any]) -> None:
        error = body["error"]
        if body["error"].get("innerError", None):
            error = body["error"]["innerError"]
        http_response_error = HttpResponseError(message="({}): {}".format(error["code"], error["message"]))
        http_response_error.error = ODataV4Format(error)  # set error.code
        raise http_response_error


class DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Document Translation API versions supported by this package"""

    #: This is the default version
    V1_0 = "1.0"


def validate_api_version(api_version: str) -> None:
    """Raise ValueError if api_version is invalid

    :param str api_version: The API version passed to the client.
    """
    if not api_version:
        return

    try:
        api_version = DocumentTranslationApiVersion(api_version)
    except ValueError as exc:
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, ", ".join(v.value for v in DocumentTranslationApiVersion)
            )
        ) from exc


def get_translation_input(args, kwargs, continuation_token):
    try:
        inputs = kwargs.pop("inputs", None)
        if not inputs:
            inputs = args[0]
        request = (
            DocumentTranslationInput._to_generated_list(inputs)  # pylint: disable=protected-access
            if not continuation_token
            else None
        )
    except (AttributeError, TypeError, IndexError):
        try:
            source_url = kwargs.pop("source_url", None)
            if not source_url:
                source_url = args[0]
            target_url = kwargs.pop("target_url", None)
            if not target_url:
                target_url = args[1]
            target_language = kwargs.pop("target_language", None)
            if not target_language:
                target_language = args[2]

            # Additional kwargs
            source_language = kwargs.pop("source_language", None)
            prefix = kwargs.pop("prefix", None)
            suffix = kwargs.pop("suffix", None)
            storage_type = kwargs.pop("storage_type", None)
            category_id = kwargs.pop("category_id", None)
            glossaries = kwargs.pop("glossaries", None)

            request = [
                _BatchRequest(
                    source=_SourceInput(
                        source_url=source_url,
                        filter=_DocumentFilter(prefix=prefix, suffix=suffix),
                        language=source_language,
                    ),
                    targets=[
                        _TargetInput(
                            target_url=target_url,
                            language=target_language,
                            glossaries=(
                                [g._to_generated() for g in glossaries]  # pylint: disable=protected-access
                                if glossaries
                                else None
                            ),
                            category=category_id,
                        )
                    ],
                    storage_type=storage_type,
                )
            ]
        except (AttributeError, TypeError, IndexError) as exc:
            raise ValueError(
                "Pass 'inputs' for multiple inputs or 'source_url', 'target_url', "
                "and 'target_language' for a single input."
            ) from exc

    return request


def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "Operation-Location",
            "Content-Encoding",
            "Vary",
            "apim-request-id",
            "X-RequestId",
            "Set-Cookie",
            "X-Powered-By",
            "Strict-Transport-Security",
            "x-content-type-options",
        }
    )
    http_logging_policy.allowed_query_params.update(
        {
            "top",
            "skip",
            "maxpagesize",
            "ids",
            "statuses",
            "createdDateTimeUtcStart",
            "createdDateTimeUtcEnd",
            "orderby",
        }
    )
    return http_logging_policy


def convert_datetime(date_time: Union[str, datetime.datetime]) -> datetime.datetime:
    if isinstance(date_time, datetime.datetime):
        return date_time
    if isinstance(date_time, str):
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    raise TypeError("Bad datetime type")


def convert_order_by(orderby: Optional[List[str]]) -> Optional[List[str]]:
    if orderby:
        orderby = [order.replace("created_on", "createdDateTimeUtc") for order in orderby]
    return orderby


class DocumentTranslationClient:
    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        """DocumentTranslationClient is your interface to the Document Translation service.
        Use the client to translate whole documents while preserving source document
        structure and text formatting.

        :param str endpoint: Supported Document Translation endpoint (protocol and hostname, for example:
            https://<resource-name>.cognitiveservices.azure.com/).
        :param credential: Credentials needed for the client to connect to Azure.
            This is an instance of AzureKeyCredential if using an API key or a token
            credential from :mod:`azure.identity`.
        :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
            :class:`~azure.core.credentials.TokenCredential`
        :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
        :paramtype api_version: str or ~azure.ai.translation.document.DocumentTranslationApiVersion

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_key]
                :end-before: [END create_dt_client_with_key]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_aad]
                :end-before: [END create_dt_client_with_aad]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with a token credential.
        """
        try:
            self._endpoint = endpoint.rstrip("/")
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc
        self._credential = credential
        self._api_version = kwargs.pop("api_version", None)
        # TODO how to support API version - v1.0 vs date-based?
        # if hasattr(self._api_version, "value"):
        #     self._api_version = cast(DocumentTranslationApiVersion, self._api_version)
        #     self._api_version = self._api_version.value
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        from ._client import DocumentTranslationClient as _BatchDocumentTranslationClient

        self._client = _BatchDocumentTranslationClient(
            endpoint=self._endpoint,
            credential=credential,
            # api_version=self._api_version,
            http_logging_policy=kwargs.pop("http_logging_policy", get_http_logging_policy()),
            polling_interval=polling_interval,
            **kwargs
        )

    def __enter__(self) -> "DocumentTranslationClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self) -> None:
        """Close the :class:`~azure.ai.translation.document.DocumentTranslationClient` session."""
        return self._client.close()

    @overload
    def begin_translation(
        self,
        source_url: str,
        target_url: str,
        target_language: str,
        *,
        source_language: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        category_id: Optional[str] = None,
        glossaries: Optional[List[TranslationGlossary]] = None,
        **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source SAS URL to the Azure Blob container containing the documents
            to be translated. See the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_url: The target SAS URL to the Azure Blob container where the translated documents
            should be written. See the service documentation for the supported SAS permissions for accessing
            target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_language: This is the language code you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :keyword str source_language: Language code for the source documents.
            If none is specified, the source language will be auto-detected for each document.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
            sub folders for translation.
        :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
            translation. This is most often use for file extensions.
        :keyword storage_type: Storage type of the input documents source string. Possible values
            include: "Folder", "File".
        :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
        :keyword str category_id: Category / custom model ID for using custom translation.
        :keyword glossaries: Glossaries to apply to translation.
        :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_translation(
        self, inputs: List[DocumentTranslationInput], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_translation(
        self, *args: Union[str, List[DocumentTranslationInput]], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source URL to the Azure Blob container containing the documents to be translated.
            This can be a SAS URL (see the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions) or a managed
            identity can be created and used to access documents in your storage account
            (see https://aka.ms/azsdk/documenttranslation/managed-identity).
        :param str target_url: The target URL to the Azure Blob container where the translated documents
            should be written. This can be a SAS URL (see the service documentation for the supported SAS permissions
            for accessing target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
            or a managed identity can be created and used to access documents in your storage account
            (see https://aka.ms/azsdk/documenttranslation/managed-identity).
        :param str target_language: This is the language code you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :keyword str source_language: Language code for the source documents.
            If none is specified, the source language will be auto-detected for each document.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
            sub folders for translation.
        :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
            translation. This is most often use for file extensions.
        :keyword storage_type: Storage type of the input documents source string. Possible values
            include: "Folder", "File".
        :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
        :keyword str category_id: Category / custom model ID for using custom translation.
        :keyword glossaries: Glossaries to apply to translation.
        :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_begin_translation.py
                :start-after: [START begin_translation]
                :end-before: [END begin_translation]
                :language: python
                :dedent: 4
                :caption: Translate the documents in your storage container.
        """

        continuation_token = kwargs.pop("continuation_token", None)

        inputs = get_translation_input(args, kwargs, continuation_token)

        def deserialization_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            translation_status = json.loads(raw_response.http_response.text())
            return self.list_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._client._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = self._client.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            DocumentTranslationLROPoller[ItemPaged[DocumentStatus]],
            self._client.begin_start_translation(
                body=_StartTranslationDetails(inputs=inputs),
                polling=DocumentTranslationLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[TranslationPolling()],
                    cont_token_response=pipeline_response,
                    **kwargs
                ),
                cls=callback,
                continuation_token=continuation_token,
                **kwargs
            ),
        )

    @distributed_trace
    def get_translation_status(self, translation_id: str, **kwargs: Any) -> TranslationStatus:
        """Gets the status of the translation operation.

        Includes the overall status, as well as a summary of
        the documents that are being translated as part of that translation operation.

        :param str translation_id: The translation operation ID.
        :return: A TranslationStatus with information on the status of the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        translation_status = self._client.get_translation_status(translation_id, **kwargs)
        return TranslationStatus._from_generated(  # pylint: disable=protected-access
            _TranslationStatus(translation_status)
        )

    @distributed_trace
    def cancel_translation(self, translation_id: str, **kwargs: Any) -> None:
        """Cancel a currently processing or queued translation operation.

        A translation will not be canceled if it is already completed, failed, or canceling.
        All documents that have completed translation will not be canceled and will be charged.
        If possible, all pending documents will be canceled.

        :param str translation_id: The translation operation ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        self._client.cancel_translation(translation_id, **kwargs)

    @distributed_trace
    def list_translation_statuses(
        self,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        translation_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        orderby: Optional[List[str]] = None,
        **kwargs: Any
    ) -> ItemPaged[TranslationStatus]:
        """List all the submitted translation operations under the Document Translation resource.

        :keyword int top: The total number of operations to return (across all pages) from all submitted translations.
        :keyword int skip: The number of operations to skip (from beginning of all submitted operations).
            By default, we sort by all submitted operations in descending order by start time.
        :keyword list[str] translation_ids: Translation operations ids to filter by.
        :keyword list[str] statuses: Translation operation statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get operations created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get operations created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] orderby: The sorting query for the operations returned. Currently only
            'created_on' supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of TranslationStatus.
        :rtype: ~azure.core.paging.ItemPaged[TranslationStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_list_translations.py
                :start-after: [START list_translations]
                :end-before: [END list_translations]
                :language: python
                :dedent: 4
                :caption: List all submitted translations under the resource.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        orderby = convert_order_by(orderby)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(
            generated_model,
        ):  # pylint: disable=protected-access
            return TranslationStatus._from_generated(
                _TranslationStatus(generated_model)
            )  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda translation_statuses: [_convert_from_generated_model(status) for status in translation_statuses],
        )

        return cast(
            ItemPaged[TranslationStatus],
            self._client.get_translations_status(
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=translation_ids,
                orderby=orderby,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def list_document_statuses(
        self,
        translation_id: str,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        document_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        orderby: Optional[List[str]] = None,
        **kwargs: Any
    ) -> ItemPaged[DocumentStatus]:
        """List all the document statuses for a given translation operation.

        :param str translation_id: ID of translation operation to list documents for.
        :keyword int top: The total number of documents to return (across all pages).
        :keyword int skip: The number of documents to skip (from beginning).
            By default, we sort by all documents in descending order by start time.
        :keyword list[str] document_ids: Document IDs to filter by.
        :keyword list[str] statuses: Document statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get documents created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get documents created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] orderby: The sorting query for the documents. Currently only
            'created_on' is supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of DocumentStatus.
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_check_document_statuses.py
                :start-after: [START list_document_statuses]
                :end-before: [END list_document_statuses]
                :language: python
                :dedent: 4
                :caption: List all the document statuses as they are being translated.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        orderby = convert_order_by(orderby)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(generated_model):
            return DocumentStatus._from_generated(_DocumentStatus(generated_model))  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses],
        )

        return cast(
            ItemPaged[DocumentStatus],
            self._client.get_documents_status(
                id=translation_id,
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=document_ids,
                orderby=orderby,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def get_document_status(self, translation_id: str, document_id: str, **kwargs: Any) -> DocumentStatus:
        """Get the status of an individual document within a translation operation.

        :param str translation_id: The translation operation ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatus with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        document_status = self._client.get_document_status(translation_id, document_id, **kwargs)
        return DocumentStatus._from_generated(_DocumentStatus(document_status))  # pylint: disable=protected-access

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        glossary_formats = self._client.get_supported_formats(type="glossary", **kwargs)
        return DocumentTranslationFileFormat._from_generated_list(  # pylint: disable=protected-access
            glossary_formats.value
        )

    @distributed_trace
    def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        document_formats = self._client.get_supported_formats(type="document", **kwargs)
        return DocumentTranslationFileFormat._from_generated_list(  # pylint: disable=protected-access
            document_formats.value
        )


__all__: List[str] = [
    "DocumentTranslationClient",
    "DocumentTranslationApiVersion",
    "DocumentTranslationLROPoller",
    # re-export models at this level for backwards compatibility
    "TranslationGlossary",
    "TranslationTarget",
    "DocumentTranslationInput",
    "TranslationStatus",
    "DocumentStatus",
    "DocumentTranslationError",
    "DocumentTranslationFileFormat",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
