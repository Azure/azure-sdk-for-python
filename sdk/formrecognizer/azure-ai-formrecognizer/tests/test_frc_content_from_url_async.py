# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormRecognizerApiVersion
from preparers import FormRecognizerPreparer, get_async_client
from asynctestcase import AsyncFormRecognizerTest
from conftest import skip_flaky_test

get_fr_client = functools.partial(get_async_client, FormRecognizerClient)


class TestContentFromUrlAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_url_auth_bad_key(self, **kwargs):
        client = get_fr_client(api_key="xxxx")
        with pytest.raises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
                result = await poller.result()

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_url_pass_stream(self):
        client = get_fr_client()
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read(4)  # makes the recording smaller

        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content_from_url(receipt)
                result = await poller.result()

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_url_transform_pdf(self):
        client = get_fr_client()
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_url_pdf(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)
        assert layout.tables[0].row_count == 3
        assert layout.tables[0].column_count== 5
        assert layout.tables[0].page_number == 1

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage_url(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf)
            result = await poller.result()
        assert len(result) == 3
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage_transform_url(self):
        client = get_fr_client()
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    async def test_content_continuation_token(self, **kwargs):
        client = get_fr_client()
        async with client:
            initial_poller = await client.begin_recognize_content_from_url(self.form_url_jpg)
            cont_token = initial_poller.continuation_token()

            poller = await client.begin_recognize_content_from_url(None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so devtools_testutils doesn't throw assertion error

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage_table_span_pdf(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_table_url_pdf)
            result = await poller.result()
        assert len(result) == 2
        layout = result[0]
        assert layout.page_number == 1
        assert len(layout.tables) == 2
        assert layout.tables[0].row_count == 29
        assert layout.tables[0].column_count== 4
        assert layout.tables[0].page_number == 1
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count== 5
        assert layout.tables[1].page_number== 1
        layout = result[1]
        assert len(layout.tables) == 1
        assert layout.page_number == 2
        assert layout.tables[0].row_count == 23
        assert layout.tables[0].column_count== 5
        assert layout.tables[0].page_number == 2
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_selection_marks(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_selection_marks_v2(self):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        async with client:
            poller = await client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_specify_pages(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1"])
            result = await poller.result()
            assert len(result) == 1

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1", "3"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2", "3"])
            result = await poller.result()
            assert len(result) == 3

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_reading_order(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.form_url_jpg, reading_order="natural")

            assert 'natural' == poller._polling_method._initial_response.http_response.request.query['readingOrder']
            result = await poller.result()
            assert result

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_language_specified(self):
        client = get_fr_client()
        async with client:
            poller = await client.begin_recognize_content_from_url(self.form_url_jpg, language="de")
            assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_language_error(self):
        client = get_fr_client()
        async with client:
            with pytest.raises(HttpResponseError) as e:
                await client.begin_recognize_content_from_url(self.form_url_jpg, language="not a language")
            assert "NotSupportedLanguage" == e.value.error.code

    @FormRecognizerPreparer()
    async def test_content_language_v2(self, **kwargs):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        async with client:
            with pytest.raises(ValueError) as e:
                await client.begin_recognize_content_from_url(self.form_url_jpg, language="en")
            assert "'language' is only available for API version V2_1 and up" in str(e.value)
