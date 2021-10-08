# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import Any, IO, Union, List, TYPE_CHECKING
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling.base_polling import LROBasePolling

from ._response_handlers import (
    prepare_prebuilt_models,
    prepare_content_result,
    prepare_form_result,
)
from ._helpers import get_content_type
from ._api_versions import FormRecognizerApiVersion
from ._form_base_client import FormRecognizerClientBase
from ._polling import AnalyzePolling

if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential, TokenCredential
    from azure.core.polling import LROPoller
    from ._models import FormPage, RecognizedForm


class FormRecognizerClient(FormRecognizerClientBase):
    """FormRecognizerClient extracts information from forms and images into structured data.
    It is the interface to use for analyzing with prebuilt models (receipts, business cards,
    invoices, identity documents), recognizing content/layout from forms, and analyzing
    custom forms from trained models. It provides different methods based on inputs from a
    URL and inputs from a stream.

    .. note:: FormRecognizerClient should be used with API versions <=v2.1.
        To use API versions 2021-09-30-preview and up, instantiate a DocumentAnalysisClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword api_version:
        The API version of the service to use for requests. It defaults to API version v2.1.
        Setting to an older version may result in reduced feature compatibility. To use the
        latest supported API version and features, instantiate a DocumentAnalysisClient instead.
    :paramtype api_version: str or ~azure.ai.formrecognizer.FormRecognizerApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.1/sample_authentication.py
            :start-after: [START create_fr_client_with_key]
            :end-before: [END create_fr_client_with_key]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.1/sample_authentication.py
            :start-after: [START create_fr_client_with_aad]
            :end-before: [END create_fr_client_with_aad]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with a token credential.
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
        api_version = kwargs.pop("api_version", FormRecognizerApiVersion.V2_1)
        super(FormRecognizerClient, self).__init__(
            endpoint=endpoint,
            credential=credential,
            api_version=api_version,
            client_kind="form",
            **kwargs
        )

    def _prebuilt_callback(
        self, raw_response, _, headers
    ):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(
            self._generated_models.AnalyzeOperationResult, raw_response
        )
        return prepare_prebuilt_models(analyze_result)

    @distributed_trace
    def begin_recognize_receipts(self, receipt, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *locale* and *pages* keyword arguments and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_receipts.py
                :start-after: [START recognize_receipts]
                :end-before: [END recognize_receipts]
                :language: python
                :dedent: 8
                :caption: Recognize sales receipt fields.
        """
        locale = kwargs.pop("locale", None)
        pages = kwargs.pop("pages", None)
        content_type = kwargs.pop("content_type", None)
        include_field_elements = kwargs.pop("include_field_elements", False)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_receipts_from_url() to analyze a receipt from a URL."
            )
        cls = kwargs.pop("cls", self._prebuilt_callback)
        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(receipt)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if locale:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"locale": locale})
            else:
                raise ValueError(
                    "'locale' is only available for API version V2_1 and up"
                )
        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )
        return self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream=receipt,
            content_type=content_type,
            include_text_details=include_field_elements,
            cls=cls,
            polling=True,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_receipts_from_url(self, receipt_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *locale* and *pages* keyword arguments and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_receipts_from_url.py
                :start-after: [START recognize_receipts_from_url]
                :end-before: [END recognize_receipts_from_url]
                :language: python
                :dedent: 8
                :caption: Recognize sales receipt fields from a URL.
        """
        locale = kwargs.pop("locale", None)
        pages = kwargs.pop("pages", None)
        include_field_elements = kwargs.pop("include_field_elements", False)
        cls = kwargs.pop("cls", self._prebuilt_callback)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if locale:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"locale": locale})
            else:
                raise ValueError(
                    "'locale' is only available for API version V2_1 and up"
                )
        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )
        return self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream={"source": receipt_url},
            include_text_details=include_field_elements,
            cls=cls,
            polling=True,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_business_cards(self, business_card, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_business_cards* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_business_cards.py
                :start-after: [START recognize_business_cards]
                :end-before: [END recognize_business_cards]
                :language: python
                :dedent: 8
                :caption: Recognize business cards from a file.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_business_cards_from_url() to analyze a business card from a URL."
            )

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(business_card)

        try:
            return self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream=business_card,
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_business_cards' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace
    def begin_recognize_business_cards_from_url(self, business_card_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_business_cards_from_url* client method

        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream={"source": business_card_url},
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_business_cards_from_url' is "
                    "only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace
    def begin_recognize_identity_documents(self, identity_document, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_identity_documents* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_identity_documents.py
                :start-after: [START recognize_identity_documents]
                :end-before: [END recognize_identity_documents]
                :language: python
                :dedent: 8
                :caption: Recognize identity document fields.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_identity_documents_from_url() to analyze an identity document from a URL."
            )
        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(identity_document)

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return self._client.begin_analyze_id_document_async(  # type: ignore
                file_stream=identity_document,
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_id_document_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_identity_documents' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace
    def begin_recognize_identity_documents_from_url(
        self, identity_document_url, **kwargs
    ):
        # type: (str, Any) -> LROPoller[List[RecognizedForm]]
        """Extract field text and semantic values from a given identity document.
        The input document must be the location (URL) of the identity document to be analyzed.

        See fields found on an identity document here:
        https://aka.ms/formrecognizer/iddocumentfields

        :param str identity_document_url: The URL of the identity document to analyze.
            The input must be a valid, encoded URL of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include all lines per page and field elements such as lines, words,
            and selection marks for each form field.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_identity_documents_from_url* client method
        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return self._client.begin_analyze_id_document_async(  # type: ignore
                file_stream={"source": identity_document_url},
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_id_document_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_identity_documents_from_url' is "
                    "only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace
    def begin_recognize_invoices(self, invoice, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages=["1-3", "5-6"]`. Separate each page number or range with a comma.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_invoices* client method

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_invoices.py
                :start-after: [START recognize_invoices]
                :end-before: [END recognize_invoices]
                :language: python
                :dedent: 8
                :caption: Recognize invoices from a file.
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_invoice_from_url() to analyze an invoice from a URL."
            )

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(invoice)

        try:
            return self._client.begin_analyze_invoice_async(  # type: ignore
                file_stream=invoice,
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_invoice_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_invoices' is only available for API version V2_1 and up"
                )
            raise e

    @distributed_trace
    def begin_recognize_invoices_from_url(self, invoice_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *begin_recognize_invoices_from_url* client method
        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return self._client.begin_analyze_invoice_async(  # type: ignore
                file_stream={"source": invoice_url},
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", self._prebuilt_callback),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_invoice_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_invoices_from_url' is "
                    "only available for API version V2_1 and up"
                )
            raise e

    def _content_callback(
        self, raw_response, _, headers
    ):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(
            self._generated_models.AnalyzeOperationResult, raw_response
        )
        return prepare_content_result(analyze_result)

    @distributed_trace
    def begin_recognize_content(self, form, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[FormPage]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: v2.1
            The *pages*, *language* and *reading_order* keyword arguments and support for image/bmp content

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_content.py
                :start-after: [START recognize_content]
                :end-before: [END recognize_content]
                :language: python
                :dedent: 8
                :caption: Recognize text and content/layout information from a form.
        """
        pages = kwargs.pop("pages", None)
        language = kwargs.pop("language", None)
        content_type = kwargs.pop("content_type", None)
        reading_order = kwargs.pop("reading_order", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_content_from_url() to analyze a document from a URL."
            )

        if content_type is None and kwargs.get("continuation_token", None) is None:
            content_type = get_content_type(form)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )

        if reading_order:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"reading_order": reading_order})
            else:
                raise ValueError(
                    "'reading_order' is only available for API version V2_1 and up"
                )

        if language:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"language": language})
            else:
                raise ValueError(
                    "'language' is only available for API version V2_1 and up"
                )

        return self._client.begin_analyze_layout_async(  # type: ignore
            file_stream=form,
            content_type=content_type,
            cls=kwargs.pop("cls", self._content_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_content_from_url(self, form_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[FormPage]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.FormPage]]
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
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )

        if reading_order:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"reading_order": reading_order})
            else:
                raise ValueError(
                    "'reading_order' is only available for API version V2_1 and up"
                )

        if language:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"language": language})
            else:
                raise ValueError(
                    "'language' is only available for API version V2_1 and up"
                )

        return self._client.begin_analyze_layout_async(  # type: ignore
            file_stream={"source": form_url},
            cls=kwargs.pop("cls", self._content_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_custom_forms(self, model_id, form, **kwargs):
        # type: (str, Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.1/sample_recognize_custom_forms.py
                :start-after: [START recognize_custom_forms]
                :end-before: [END recognize_custom_forms]
                :language: python
                :dedent: 8
                :caption: Recognize fields and values from a custom form.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        pages = kwargs.pop("pages", None)
        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval
        )
        continuation_token = kwargs.pop("continuation_token", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError(
                "Call begin_recognize_custom_forms_from_url() to analyze a document from a URL."
            )
        if content_type is None and continuation_token is None:
            content_type = get_content_type(form)

        include_field_elements = kwargs.pop("include_field_elements", False)

        def analyze_callback(
            raw_response, _, headers
        ):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(
                self._generated_models.AnalyzeOperationResult, raw_response
            )
            return prepare_form_result(analyze_result, model_id)

        callback = kwargs.pop("cls", analyze_callback)
        polling = LROBasePolling(
            timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs
        )

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )

        return self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream=form,
            model_id=model_id,
            include_text_details=include_field_elements,
            content_type=content_type,
            cls=callback,
            polling=polling,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_custom_forms_from_url(self, model_id, form_url, **kwargs):
        # type: (str, str, Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        pages = kwargs.pop("pages", None)
        continuation_token = kwargs.pop("continuation_token", None)
        include_field_elements = kwargs.pop("include_field_elements", False)
        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval
        )

        def analyze_callback(
            raw_response, _, headers
        ):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(
                self._generated_models.AnalyzeOperationResult, raw_response
            )
            return prepare_form_result(analyze_result, model_id)

        callback = kwargs.pop("cls", analyze_callback)
        polling = LROBasePolling(
            timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs
        )

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self._api_version == FormRecognizerApiVersion.V2_1:
                kwargs.update({"pages": pages})
            else:
                raise ValueError(
                    "'pages' is only available for API version V2_1 and up"
                )

        return self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream={"source": form_url},
            model_id=model_id,
            include_text_details=include_field_elements,
            cls=callback,
            polling=polling,
            continuation_token=continuation_token,
            **kwargs
        )

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.formrecognizer.FormRecognizerClient` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> FormRecognizerClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
