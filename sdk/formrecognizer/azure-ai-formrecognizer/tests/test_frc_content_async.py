# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from preparers import FormRecognizerPreparer, get_async_client
from asynctestcase import AsyncFormRecognizerTest
from conftest import skip_flaky_test

get_fr_client = functools.partial(get_async_client, FormRecognizerClient)


class TestContentFromStreamAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_content_bad_endpoint(self, **kwargs):
        formrecognizer_test_api_key = "fakeZmFrZV9hY29jdW50X2tleQ=="
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_content(my_file)
                result = await poller.result()

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_authentication_bad_key(self, **kwargs):
        client = get_fr_client(api_key="xxxx")
        with pytest.raises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_content(b"xxx", content_type="application/pdf")
                result = await poller.result()

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_passing_enum_content_type(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_recognize_content(
                my_file,
                content_type=FormContentType.APPLICATION_PDF
            )
            result = await poller.result()
        assert result is not None

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_damaged_file_passed_as_bytes(self):
        client = get_fr_client()
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content(
                    damaged_pdf,
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    async def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    my_file,
                    content_type="application/jpeg"
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    async def test_auto_detect_unsupported_stream_content(self, **kwargs):
        client = get_fr_client()
        with open(self.unsupported_content_py, "rb") as fd:
            my_file = fd.read()

        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    my_file
                )
                result = await poller.result()

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_stream_transform_pdf(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(form, cls=callback)
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
    @recorded_by_proxy_async
    async def test_content_stream_transform_jpg(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(form, cls=callback)
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
    @recorded_by_proxy_async
    async def test_content_stream_jpg(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            form = fd.read()

        async with client:
            poller = await client.begin_recognize_content(form)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)
        assert layout.tables[0].row_count == 5
        assert layout.tables[0].column_count== 4
        assert layout.tables[1].row_count == 4
        assert layout.tables[1].column_count== 2
        assert layout.tables[0].page_number == 1
        assert layout.tables[1].page_number== 1

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            invoice = fd.read()
        async with client:
            poller = await client.begin_recognize_content(invoice)
            result = await poller.result()

        assert len(result) == 3
        self.assertFormPagesHasValues(result)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage_transform(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(form, cls=callback)
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
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with client:
            initial_poller = await client.begin_recognize_content(my_file)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_content(None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so devtools_testutils doesn't throw assertion error


    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_multipage_table_span_pdf(self):
        client = get_fr_client()
        with open(self.multipage_table_pdf, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_recognize_content(my_file)
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

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_selection_marks(self):
        client = get_fr_client()
        with open(self.selection_form_pdf, "rb") as fd:
            form = fd.read()

        async with client:
            poller = await client.begin_recognize_content(form)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @pytest.mark.skip()
    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_selection_marks_v2(self):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        with open(self.selection_form_pdf, "rb") as fd:
            form = fd.read()

        async with client:
            poller = await client.begin_recognize_content(form)
            result = await poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_specify_pages(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            form = fd.read()

        async with client:
            poller = await client.begin_recognize_content(form, pages=["1"])
            result = await poller.result()
            assert len(result) == 1

            poller = await client.begin_recognize_content(form, pages=["1", "3"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content(form, pages=["1-2"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content(form, pages=["1-2", "3"])
            result = await poller.result()
            assert len(result) == 3

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_reading_order(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            form = fd.read()

        async with client:
            poller = await client.begin_recognize_content(form, reading_order="natural")

            assert 'natural' == poller._polling_method._initial_response.http_response.request.query['readingOrder']
            result = await poller.result()
            assert result

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_content_language_specified(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_recognize_content(my_file, language="de")
            assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    async def test_content_language_v2(self, **kwargs):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        async with client:
            with pytest.raises(ValueError) as e:
                await client.begin_recognize_content(my_file, language="en")
            assert "'language' is only available for API version V2_1 and up" in str(e.value)
