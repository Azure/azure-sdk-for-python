# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (
    Any,
    IO,
    Union,
    List
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._response_handlers import (
    prepare_prebuilt_models,
    prepare_content_result,
    prepare_form_result
)
from .._helpers import get_content_type
from .._api_versions import FormRecognizerApiVersion
from .._polling import AnalyzePolling
from ._form_base_client_async import FormRecognizerClientBaseAsync
from .._models import FormPage, RecognizedForm


class FormRecognizerClient(FormRecognizerClientBaseAsync):
    """FormRecognizerClient extracts information from forms and images into structured data.
    It is the interface to use for analyzing receipts, recognizing content/layout from
    forms, and analyzing custom forms from trained models. It provides different methods
    based on inputs from a URL and inputs from a stream.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        or :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.formrecognizer.FormRecognizerApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_fr_client_with_key_async]
            :end-before: [END create_fr_client_with_key_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_fr_client_with_aad_async]
            :end-before: [END create_fr_client_with_aad_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with a token credential.
    """

    def _prebuilt_callback(self, raw_response, _, headers, **kwargs):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
        return prepare_prebuilt_models(analyze_result, **kwargs)

    @distributed_trace_async
    async def begin_recognize_receipts(
            self,
            receipt: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given sales receipt.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on a receipt here:
        https://aka.ms/formrecognizer/receiptfields

        :param receipt: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type receipt: bytes or IO[bytes]
        :keyword bool include_field_elements:
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword str locale: Locale of the receipt. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:
        .. versionadded:: v2.1-preview
            The *locale* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_receipts_async.py
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
        if content_type is None:
            content_type = get_content_type(receipt)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if locale:
            if self.api_version == FormRecognizerApiVersion.V2_1_PREVIEW:
                kwargs.update({"locale": locale})
            else:
                raise ValueError("'locale' is only available for API version V2_1_PREVIEW and up")

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream=receipt,
            content_type=content_type,
            include_text_details=include_field_elements,
            cls=kwargs.pop("cls", self._prebuilt_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_receipts_from_url(
            self,
            receipt_url: str,
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given sales receipt.
        The input document must be the location (URL) of the receipt to be analyzed.

        See fields found on a receipt here:
        https://aka.ms/formrecognizer/receiptfields

        :param str receipt_url: The URL of the receipt to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword str locale: Locale of the receipt. Supported locales include: en-US, en-AU, en-CA, en-GB,
            and en-IN.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:
        .. versionadded:: v2.1-preview
            The *locale* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_receipts_from_url_async.py
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
            if self.api_version == FormRecognizerApiVersion.V2_1_PREVIEW:
                kwargs.update({"locale": locale})
            else:
                raise ValueError("'locale' is only available for API version V2_1_PREVIEW and up")

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream={"source": receipt_url},
            include_text_details=include_field_elements,
            cls=kwargs.pop("cls", self._prebuilt_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_business_cards(
            self,
            business_card: Union[bytes, IO[bytes]],
            **kwargs: Any
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
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_business_cards_async.py
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

        if content_type is None:
            content_type = get_content_type(business_card)

        try:
            return await self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream=business_card,
                content_type=content_type,
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", lambda pipeline_response, _, response_headers: self._prebuilt_callback(
                    pipeline_response, _, response_headers, business_card=True
                )),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_business_cards' is only available for API version V2_1_PREVIEW and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_business_cards_from_url(
            self,
            business_card_url: str,
            **kwargs: Any
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
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return await self._client.begin_analyze_business_card_async(  # type: ignore
                file_stream={"source": business_card_url},
                include_text_details=include_field_elements,
                cls=kwargs.pop("cls", lambda pipeline_response, _, response_headers: self._prebuilt_callback(
                    pipeline_response, _, response_headers, business_card=True
                )),
                polling=True,
                **kwargs
            )
        except ValueError as e:
            if "begin_analyze_business_card_async" in str(e):
                raise ValueError(
                    "Method 'begin_recognize_business_cards_from_url' is only available for "
                    "API version V2_1_PREVIEW and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_invoices(
            self,
            invoice: str,
            **kwargs: Any
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
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:


        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_invoices_async.py
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

        if content_type is None:
            content_type = get_content_type(invoice)

        try:
            return await self._client.begin_analyze_invoice_async(  # type: ignore
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
                    "Method 'begin_recognize_invoices' is only available for API version V2_1_PREVIEW and up"
                )
            raise e

    @distributed_trace_async
    async def begin_recognize_invoices_from_url(
            self,
            invoice_url: str,
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Extract field text and semantic values from a given invoice.
        The input document must be the location (URL) of the invoice to be analyzed.

        See fields found on a invoice card here:
        https://aka.ms/formrecognizer/invoicefields

        :param str invoice_url: The URL of the invoice to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword str locale: Locale of the invoice. Supported locales include: en-US
        :keyword bool include_field_elements:
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        include_field_elements = kwargs.pop("include_field_elements", False)

        try:
            return await self._client.begin_analyze_invoice_async(  # type: ignore
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
                    "only available for API version V2_1_PREVIEW and up"
                )
            raise e

    def _content_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
        return prepare_content_result(analyze_result)

    @distributed_trace_async
    async def begin_recognize_content(
            self,
            form: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[FormPage]]:
        """Extract text and content/layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        :param form: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF), input the number of the
            pages you want to get OCR result. For a range of pages, use a hyphen. Separate each page or
            range with a comma.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:
        .. versionadded:: v2.1-preview
            The *pages* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_content_async.py
                :start-after: [START recognize_content_async]
                :end-before: [END recognize_content_async]
                :language: python
                :dedent: 8
                :caption: Recognize text and content/layout information from a form.
        """
        pages = kwargs.pop("pages", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_content_from_url() to analyze a document from a URL.")

        if content_type is None:
            content_type = get_content_type(form)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self.api_version == FormRecognizerApiVersion.V2_1_PREVIEW:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1_PREVIEW and up")

        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream=form,
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
        :keyword list[str] pages: Custom page numbers for multi-page documents(PDF/TIFF), input the number of the
            pages you want to get OCR result. For a range of pages, use a hyphen. Separate each page or
            range with a comma.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:
        .. versionadded:: v2.1-preview
            The *pages* keyword argument
        """
        pages = kwargs.pop("pages", None)

        # FIXME: part of this code will be removed once autorest can handle diff mixin
        # signatures across API versions
        if pages:
            if self.api_version == FormRecognizerApiVersion.V2_1_PREVIEW:
                kwargs.update({"pages": pages})
            else:
                raise ValueError("'pages' is only available for API version V2_1_PREVIEW and up")

        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream={"source": form_url},
            cls=kwargs.pop("cls", self._content_callback),
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms(
            self,
            model_id: str,
            form: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        :param str model_id: Custom model identifier.
        :param form: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword bool include_field_elements:
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword content_type: Content-type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :paramtype content_type: str or ~azure.ai.formrecognizer.FormContentType
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_custom_forms_async.py
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

        include_field_elements = kwargs.pop("include_field_elements", False)

        if content_type is None:
            content_type = get_content_type(form)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream=form,
            model_id=model_id,
            include_text_details=include_field_elements,
            content_type=content_type,
            cls=kwargs.pop("cls", analyze_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[AnalyzePolling()],
                **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms_from_url(
            self,
            model_id: str,
            form_url: str,
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be the location (URL) of the document to be analyzed.

        :param str model_id: Custom model identifier.
        :param str form_url: The URL of the form to analyze. The input must be a valid, encoded URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword bool include_field_elements:
            Whether or not to include field elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")
        polling_interval = kwargs.pop("polling_interval", self._client._config.polling_interval)
        continuation_token = kwargs.pop("continuation_token", None)
        include_field_elements = kwargs.pop("include_field_elements", False)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._deserialize(self._generated_models.AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream={"source": form_url},
            model_id=model_id,
            include_text_details=include_field_elements,
            cls=kwargs.pop("cls", analyze_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[AnalyzePolling()],
                **kwargs
            ),
            continuation_token=continuation_token,
            **kwargs
        )

    async def __aenter__(self) -> "FormRecognizerClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.aio.FormRecognizerClient` session.
        """
        await self._client.__aexit__()
