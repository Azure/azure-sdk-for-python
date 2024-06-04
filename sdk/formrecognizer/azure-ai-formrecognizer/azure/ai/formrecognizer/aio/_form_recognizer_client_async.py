# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import Any, IO, Union, List
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._response_handlers import (
    prepare_prebuilt_models,
    prepare_content_result,
    prepare_form_result,
)
from .._helpers import get_content_type
from .._api_versions import FormRecognizerApiVersion
from .._polling import AnalyzePolling
from ._form_base_client_async import FormRecognizerClientBaseAsync
from .._models import FormPage, RecognizedForm


class FormRecognizerClient(FormRecognizerClientBaseAsync):
    """FormRecognizerClient extracts information from forms and images into structured data.
    It is the interface to use for analyzing with prebuilt models (receipts, business cards,
    invoices, identity documents), recognizing content/layout from forms, and analyzing
    custom forms from trained models. It provides different methods based on inputs from a
    URL and inputs from a stream.

    .. note:: FormRecognizerClient should be used with API versions <=v2.1.
        To use API versions 2022-08-31 and up, instantiate a DocumentAnalysisClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        or :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :keyword api_version:
        The API version of the service to use for requests. It defaults to API version v2.1.
        Setting to an older version may result in reduced feature compatibility. To use the
        latest supported API version and features, instantiate a DocumentAnalysisClient instead.
    :paramtype api_version: str or ~azure.ai.formrecognizer.FormRecognizerApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.1/async_samples/sample_authentication_v3_1_async.py
            :start-after: [START create_fr_client_with_key_async]
            :end-before: [END create_fr_client_with_key_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.1/async_samples/sample_authentication_v3_1_async.py
            :start-after: [START create_fr_client_with_aad_async]
            :end-before: [END create_fr_client_with_aad_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with a token credential.
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        api_version = kwargs.pop("api_version", FormRecognizerApiVersion.V2_1)
        super().__init__(
            endpoint=endpoint, credential=credential, api_version=api_version, client_kind="form", **kwargs
        )

    def _prebuilt_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
        return prepare_prebuilt_models(analyze_result)

    @distributed_trace_async
    async def begin_recognize_receipts(
        self, receipt: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given sales receipt.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on a receipt here:
        https://aka.ms/formrecognizer/receiptfields

        :param receipt: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type receipt: bytes or IO[bytes]
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword str locale: Locale of the receipt. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *locale* keyword argument and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_receipts_async.py
                :start-after: [START recognize_receipts_async]
                :end-before: [END recognize_receipts_async]
                :language: python
                :dedent: 8
                :caption: Recognize sales receipt fields.
        """
        locale = kwargs.pop("locale", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_receipts_from_url() to analyze a receipt from a URL.")

        include_field_elements = kwargs.pop("include_field_elements", False)
        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(receipt)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if locale:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"locale": locale})
            else:
                raise ValueError("'locale' is only available for API version V2_1 and up")

        pages = kwargs.pop("pages", None)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream=receipt,  # type: ignore
            content_type=content_type,
            include_text_details=include_field_elements,
            cls=kwargs.pop("cls", self._prebuilt_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_receipts_from_url(
        self, receipt_url: str, **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given sales receipt.
        The input document must be the location (URL) of the receipt to be analyzed.

        See fields found on a receipt here:
        https://aka.ms/formrecognizer/receiptfields

        :param str receipt_url: The URL of the receipt to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword str locale: Locale of the receipt. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *locale* keyword argument and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_receipts_from_url_async.py
                :start-after: [START recognize_receipts_from_url_async]
                :end-before: [END recognize_receipts_from_url_async]
                :language: python
                :dedent: 8
                :caption: Recognize sales receipt fields from a URL.
        """
        locale = kwargs.pop("locale", None)

        include_field_elements = kwargs.pop("include_field_elements", False)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if locale:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"locale": locale})
            else:
                raise ValueError("'locale' is only available for API version V2_1 and up")

        pages = kwargs.pop("pages", None)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream={"source": receipt_url},  # type: ignore
            include_text_details=include_field_elements,
            cls=kwargs.pop("cls", self._prebuilt_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_business_cards(
        self, business_card: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given business card.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on a business card here:
        https://aka.ms/formrecognizer/businesscardfields

        :param business_card: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type business_card: bytes or IO[bytes]
        :keyword str locale: Locale of the business card. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_business_cards* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_business_cards_async.py
                :start-after: [START recognize_business_cards_async]
                :end-before: [END recognize_business_cards_async]
                :language: python
                :dedent: 8
                :caption: Recognize business cards from a file.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_business_cards_from_url() to analyze a business card from a URL.")

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(business_card)

        try:
            return await self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream=business_card,  # type: ignore
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Method 'begin_recognize_business_cards' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_business_cards_from_url(
        self, business_card_url: str, **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given business card.
        The input document must be the location (URL) of the card to be analyzed.

        See fields found on a business card here:
        https://aka.ms/formrecognizer/businesscardfields

        :param str business_card_url: The URL of the business card to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword str locale: Locale of the business card. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_business_cards_from_url* client method

        """
        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return await self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream={"source": business_card_url},  # type: ignore
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Method 'begin_recognize_business_cards_from_url' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_identity_documents(
        self, identity_document: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given identity document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on an identity document here:
        https://aka.ms/formrecognizer/iddocumentfields

        :param identity_document: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type identity_document: bytes or IO[bytes]
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_identity_documents* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_identity_documents_async.py
                :start-after: [START recognize_identity_documents_async]
                :end-before: [END recognize_identity_documents_async]
                :language: python
                :dedent: 8
                :caption: Recognize identity documents from a file.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_identity_documents_from_url() to analyze an identity document from a URL."
            )

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(identity_document)

        try:
            return await self._client.begin_analyze_id_document_async(  # type: ignore
                file_stream=identity_document,  # type: ignore
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_id_document_async" in str(e):
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Method 'begin_recognize_identity_documents' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_identity_documents_from_url(  # pylint: disable=name-too-long
        self, identity_document_url: str, **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given identity document.
        The input document must be the location (URL) of the identity document to be analyzed.

        See fields found on an identity document here:
        https://aka.ms/formrecognizer/iddocumentfields

        :param str identity_document_url: The URL of the identity document to analyze. The input must be a valid,
            encoded URL of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_identity_documents_from_url* client method
        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return await self._client.begin_analyze_id_document_async(  # type: ignore
                file_stream={"source": identity_document_url},  # type: ignore
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_id_document_async" in str(e):
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Method 'begin_recognize_identity_documents_from_url' is "
                    "only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_invoices(
        self, invoice: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given invoice.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on a invoice here:
        https://aka.ms/formrecognizer/invoicefields

        :param invoice: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type invoice: bytes or IO[bytes]
        :keyword str locale: Locale of the invoice. Supported locales include: en-US
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_invoices* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_invoices_async.py
                :start-after: [START recognize_invoices_async]
                :end-before: [END recognize_invoices_async]
                :language: python
                :dedent: 8
                :caption: Recognize invoices from a file.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_invoice_from_url() to analyze an invoice from a URL.")

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(invoice)

        try:
            return await self._client.begin_analyze_invoice_async(  # type: ignore
                file_stream=invoice,  # type: ignore
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_invoice_async" in str(e):
                raise ValueError("Method 'begin_recognize_invoices' is only available for API version V2_1 and up")  # pylint: disable=raise-missing-from
            raise e

    @distributed_trace_async
    async def begin_recognize_invoices_from_url(
        self, invoice_url: str, **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given invoice.
        The input document must be the location (URL) of the invoice to be analyzed.

        See fields found on a invoice card here:
        https://aka.ms/formrecognizer/invoicefields

        :param str invoice_url: The URL of the invoice to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword str locale: Locale of the invoice. Supported locales include: en-US
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_invoices_from_url* client method
        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return await self._client.begin_analyze_invoice_async(  # type: ignore
                file_stream={"source": invoice_url},  # type: ignore
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_invoice_async" in str(e):
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Method 'begin_recognize_invoices_from_url' is only available for API version V2_1 and up"
                )
            raise e

    def _content_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
        return prepare_content_result(analyze_result)

    @distributed_trace_async
    async def begin_recognize_content(
        self, form: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[FormPage]]:
        """Extract text and content/layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        :param form: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str language: The BCP-47 language code of the text in the document.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/form-recognizer/language-support.
            Content supports auto language identification and multilanguage documents, so only
            provide a language code if you would like to force the documented to be processed as
            that specific language.
        :keyword str reading_order: Reading order algorithm to sort the text lines returned. Supported
            reading orders include: basic (default), natural. Set 'basic' to sort lines left to right and top
            to bottom, although in some cases proximity is treated with higher priority. Set 'natural' to sort
            lines by using positional information to keep nearby lines together.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *pages*, *language* and *reading_order* keyword arguments and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_content_async.py
                :start-after: [START recognize_content_async]
                :end-before: [END recognize_content_async]
                :language: python
                :dedent: 8
                :caption: Recognize text and content/layout information from a form.
        """
        pages = kwargs.pop("pages", None)
        language = kwargs.pop("language", None)
        reading_order = kwargs.pop("reading_order", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_content_from_url() to analyze a document from a URL.")

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(form)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        if reading_order:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"reading_order": reading_order})
            else:
                raise ValueError("'reading_order' is only available for API version V2_1 and up")

        if language:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"language": language})
            else:
                raise ValueError("'language' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream=form,  # type: ignore
            content_type=content_type,
            cls=kwargs.pop("cls", self._content_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_content_from_url(self, form_url: str, **kwargs: Any) -> AsyncLROPoller[List[FormPage]]:
        """Extract text and layout information from a given document.
        The input document must be the location (URL) of the document to be analyzed.

        :param str form_url: The URL of the form to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str language: The BCP-47 language code of the text in the document.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/form-recognizer/language-support.
            Content supports auto language identification and multilanguage documents, so only
            provide a language code if you would like to force the documented to be processed as
            that specific language.
        :keyword str reading_order: Reading order algorithm to sort the text lines returned. Supported
            reading orders include: basic (default), natural. Set 'basic' to sort lines left to right and top
            to bottom, although in some cases proximity is treated with higher priority. Set 'natural' to sort
            lines by using positional information to keep nearby lines together.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *pages*, *language* and *reading_order* keyword arguments and support for image/bmp content
        """
        pages = kwargs.pop("pages", None)
        language = kwargs.pop("language", None)
        reading_order = kwargs.pop("reading_order", None)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        if reading_order:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"reading_order": reading_order})
            else:
                raise ValueError("'reading_order' is only available for API version V2_1 and up")

        if language:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"language": language})
            else:
                raise ValueError("'language' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream={"source": form_url},  # type: ignore
            cls=kwargs.pop("cls", self._content_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms(
        self, model_id: str, form: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff', or 'image/bmp'.

        :param str model_id: Custom model identifier.
        :param form: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/async_samples/sample_recognize_custom_forms_async.py
                :start-after: [START recognize_custom_forms_async]
                :end-before: [END recognize_custom_forms_async]
                :language: python
                :dedent: 8
                :caption: Recognize fields and values from a custom form.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)
        content_type = kwargs.pop("content_type", None)
        continuation_token = kwargs.pop("continuation_token", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_custom_forms_from_url() to analyze a document from a URL.")
        if content_type is None and continuation_token is None:
            content_type = get_content_type(form)

        pages = kwargs.pop("pages", None)
        include_field_elements = kwargs.pop("include_field_elements", False)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        callback = kwargs.pop("cls", analyze_callback)
        polling: AsyncLROBasePolling = AsyncLROBasePolling(
            timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs
        )

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream=form,  # type: ignore
            model_id=model_id,
            include_text_details=include_field_elements,
            content_type=content_type,
            cls=callback,
            polling=polling,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms_from_url(
        self, model_id: str, form_url: str, **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be the location (URL) of the document to be analyzed.

        :param str model_id: Custom model identifier.
        :param str form_url: The URL of the form to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")
        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)

        pages = kwargs.pop("pages", None)
        continuation_token = kwargs.pop("continuation_token", None)
        include_field_elements = kwargs.pop("include_field_elements", False)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        callback = kwargs.pop("cls", analyze_callback)
        polling: AsyncLROBasePolling = AsyncLROBasePolling(
            timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs
        )

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1 and up")

        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream={"source": form_url},  # type: ignore
            model_id=model_id,
            include_text_details=include_field_elements,
            cls=callback,
            polling=polling,
            continuation_token=continuation_token,
            **kwargs
        )

    async def __aenter__(self) -> "FormRecognizerClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.aio.FormRecognizerClient` session."""
        await self._client.__aexit__()
