# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date, time
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer.aio import DocumentAnalysisClient
from azure.ai.formrecognizer import AnalyzeResult
from azure.ai.formrecognizer._generated.v2022_01_30_preview.models import AnalyzeResultOperation
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestDACAnalyzePrebuiltsFromUrlAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_business_card_multipage_pdf(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-businessCard", self.business_card_multipage_url_pdf)
            result = await poller.result()

        assert len(result.documents) == 2
        business_card = result.documents[0]
        assert len(business_card.fields.get("ContactNames").value) == 1
        assert business_card.fields.get("ContactNames").value[0].value['FirstName'].value == 'JOHN'
        assert business_card.fields.get("ContactNames").value[0].value['LastName'].value == 'SINGER'

        assert len(business_card.fields.get("JobTitles").value) == 1
        assert business_card.fields.get("JobTitles").value[0].value == "Software Engineer"

        assert len(business_card.fields.get("Emails").value) == 1
        assert business_card.fields.get("Emails").value[0].value == "johnsinger@contoso.com"

        assert len(business_card.fields.get("Websites").value) == 1
        assert business_card.fields.get("Websites").value[0].value == "https://www.contoso.com"

        # FIXME: the service is not returning this currently
        # assert len(business_card.fields.get("OtherPhones").value) == 1
        # assert business_card.fields.get("OtherPhones").value[0].value == "+14257793479"

        business_card = result.documents[1]
        assert len(business_card.fields.get("ContactNames").value) == 1
        assert business_card.fields.get("ContactNames").value[0].value['FirstName'].value == 'Avery'
        assert business_card.fields.get("ContactNames").value[0].value['LastName'].value == 'Smith'

        assert len(business_card.fields.get("JobTitles").value) == 1
        assert business_card.fields.get("JobTitles").value[0].value == "Senior Researcher"

        assert len(business_card.fields.get("Departments").value) == 1
        assert business_card.fields.get("Departments").value[0].value == "Cloud & Al Department"

        assert len(business_card.fields.get("Emails").value) == 1
        assert business_card.fields.get("Emails").value[0].value == "avery.smith@contoso.com"

        assert len(business_card.fields.get("Websites").value) == 1
        assert business_card.fields.get("Websites").value[0].value == "https://www.contoso.com/"

        # The phone number values are not getting normalized to a phone number type. Just assert on text.
        assert len(business_card.fields.get("MobilePhones").value) == 1
        assert business_card.fields.get("MobilePhones").value[0].content == "+44 (0) 7911 123456"

        assert len(business_card.fields.get("WorkPhones").value) == 1
        assert business_card.fields.get("WorkPhones").value[0].content == "+44 (0) 20 9876 5432"

        assert len(business_card.fields.get("Faxes").value) == 1
        assert business_card.fields.get("Faxes").value[0].content == "+44 (0) 20 6789 2345"

        assert len(business_card.fields.get("Addresses").value) == 1
        assert business_card.fields.get("Addresses").value[0].value == "2 Kingdom Street Paddington, London, W2 6BD"

        assert len(business_card.fields.get("CompanyNames").value) == 1
        assert business_card.fields.get("CompanyNames").value[0].value == "Contoso"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_identity_document_jpg_passport(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-idDocument", self.identity_document_url_jpg_passport)

            result = await poller.result()
            assert len(result.documents) == 1
        
            id_document = result.documents[0]
            # check dict values

            passport = id_document.fields.get("MachineReadableZone").value
            assert passport["LastName"].value == "MARTIN"
            assert passport["FirstName"].value == "SARAH"
            assert passport["DocumentNumber"].value == "ZE000509"
            assert passport["DateOfBirth"].value == date(1985,1,1)
            assert passport["DateOfExpiration"].value == date(2023,1,14)
            assert passport["Sex"].value == "F"
            assert passport["CountryRegion"].value == "CAN"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_identity_document_jpg(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-idDocument", self.identity_document_url_jpg)

            result = await poller.result()
        assert len(result.documents) == 1
        id_document = result.documents[0]

        # check dict values
        assert id_document.fields.get("LastName").value == "TALBOT"
        assert id_document.fields.get("FirstName").value == "LIAM R."
        assert id_document.fields.get("DocumentNumber").value == "WDLABCD456DG"
        assert id_document.fields.get("DateOfBirth").value == date(1958,1,6)
        assert id_document.fields.get("DateOfExpiration").value == date(2020,8,12)
        assert id_document.fields.get("Sex").value == "M"
        assert id_document.fields.get("Address").value == "123 STREET ADDRESS YOUR CITY WA 99999-1234"
        assert id_document.fields.get("CountryRegion").value == "USA"
        assert id_document.fields.get("Region").value == "Washington"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_tiff(self, client, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_analyze_document_from_url(model="prebuilt-invoice", document_url=self.invoice_url_tiff)

            result = await poller.result()
        assert len(result.documents) == 1
        invoice = result.documents[0]

        # check dict values
        assert invoice.fields.get("VendorName").value ==  "Contoso"
        assert invoice.fields.get("VendorAddress").value, '1 Redmond way Suite 6000 Redmond ==  WA 99243'
        assert invoice.fields.get("CustomerAddressRecipient").value ==  "Microsoft"
        assert invoice.fields.get("CustomerAddress").value, '1020 Enterprise Way Sunnayvale ==  CA 87659'
        assert invoice.fields.get("CustomerName").value ==  "Microsoft"
        assert invoice.fields.get("InvoiceId").value ==  '34278587'
        assert invoice.fields.get("InvoiceDate").value, date(2017, 6 ==  18)
        assert invoice.fields.get("Items").value[0].value["Amount"].value.amount ==  56651.49
        assert invoice.fields.get("Items").value[0].value["Amount"].value.symbol ==  "$"
        assert invoice.fields.get("DueDate").value, date(2017, 6 ==  24)

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        assert client._client._config.polling_interval ==  7

        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, polling_interval=6)
            await poller.wait()
            assert poller._polling_method._timeout ==  6
            poller2 = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
            await poller2.wait()
            assert poller2._polling_method._timeout ==  7  # goes back to client default

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    async def test_active_directory_auth_async(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentAnalysisClient(endpoint, token)
        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.receipt_url_jpg
            )
            result = await poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipts_encoded_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError) as e:
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", "https://fakeuri.com/blank%20space")
        assert "https://fakeuri.com/blank%20space" in  e.value.response.request.body

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(ServiceRequestError):
            client = DocumentAnalysisClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_analyze_document_from_url(
                    "prebuilt-receipt",
                    self.receipt_url_jpg
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_analyze_document_from_url(
                    "prebuilt-receipt",
                    self.receipt_url_jpg
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_bad_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", "https://badurl.jpg")
                result = await poller.result()

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_pass_stream(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        with open(self.receipt_png, "rb") as fd:
            receipt = fd.read(4)  # makes the recording smaller

        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", receipt)
                result = await poller.result()

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_transform_jpg(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.receipt_url_jpg,
                cls=callback
            )
            result = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_png(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_png)
            result = await poller.result()

        assert len(result.documents) == 1
        receipt = result.documents[0]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("Subtotal").value ==  1098.99
        assert receipt.fields.get("TotalTax").value ==  104.4
        assert receipt.fields.get("Total").value ==  1203.39
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type == "receipt.retailMeal"

        assert len(result.pages) == 1

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_multipage_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.multipage_receipt_url_pdf)
            result = await poller.result()

        assert len(result.documents) == 2
        receipt = result.documents[0]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("MerchantPhoneNumber").value ==  '+19876543210'
        assert receipt.fields.get("Subtotal").value ==  11.7
        assert receipt.fields.get("TotalTax").value ==  1.17
        assert receipt.fields.get("Tip").value ==  1.63
        assert receipt.fields.get("Total").value ==  14.5
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type == "receipt.retailMeal"
        receipt = result.documents[1]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("Subtotal").value ==  1098.99
        assert receipt.fields.get("TotalTax").value ==  104.4
        assert receipt.fields.get("Total").value ==  1203.39
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type == "receipt.retailMeal"

        assert len(result.pages) == 2

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_multipage_transform_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.multipage_receipt_url_pdf,
                cls=callback
            )

            result = await poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    async def test_receipt_continuation_token(self, **kwargs):
        client = kwargs.pop("client")

        async with client:
            initial_poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_locale_specified(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, locale="en-IN")
            assert 'en-IN' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_locale_error(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, locale="not a locale")
        assert "InvalidArgument" == e.value.error.code

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, pages="1")
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
